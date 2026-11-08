/*
 * PERF-01C read-only MATLAB in-process BLAS/MKL inspection MEX.
 * Diagnostic ONLY: no timers, BLAS replacement, or thread-setting API.
 * mkl_get_max_threads gives TARGET max threads, NOT active workers.
 *
 * Uses RTLD_NOLOAD: no new BLAS libraries can be initialized by this probe.
 * Preserve original frozen MATLAB source; compile probe outside repository.
 */
#include "mex.h"
#include <ctype.h>
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define MAPS_BUF_SIZE 524288
#define PATH_LIMIT 4096
typedef int (*mkl_max_threads_fn)(void);
typedef int (*omp_max_threads_fn)(void);

static int matched_library(const char *src) {
    /* Match the actual shared-library BASENAME, never directory names
       (for example 'component' was a false OpenMP path match). */
    const char *base = strrchr(src, '/');
    char lower[PATH_LIMIT];
    size_t n, i;
    base = base ? base + 1 : src;
    n = strlen(base);
    if (n >= sizeof(lower)) n = sizeof(lower) - 1;
    for (i = 0; i < n; ++i) lower[i] = (char)tolower((unsigned char)base[i]);
    lower[n] = '\0';
    /* Prefixes only: 'libmwagentspflegacyservicepublisher.so' contains
       'blis' within 'publisher' and is NOT a BLIS library. */
    return strcmp(lower, "mkl.so") == 0 ||
           strncmp(lower, "libmkl", 6) == 0 ||
           strncmp(lower, "libmwblas", 9) == 0 ||
           strncmp(lower, "libmwgraphblas", 14) == 0 ||
           strncmp(lower, "libblas", 7) == 0 ||
           strncmp(lower, "libblis", 7) == 0 ||
           strncmp(lower, "libaocl", 7) == 0 ||
           strncmp(lower, "libiomp", 7) == 0 ||
           strncmp(lower, "libgomp", 7) == 0 ||
           strncmp(lower, "libomp", 6) == 0 ||
           strncmp(lower, "libmwomp", 8) == 0;
}

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]) {
    FILE *maps;
    char line[8192];
    char paths[MAPS_BUF_SIZE];
    char sym_source[PATH_LIMIT], omp_source[PATH_LIMIT];
    int target = -1, symbol_found = 0, seen = 0;
    int omp_target = -1, omp_found = 0;
    mkl_max_threads_fn mk = NULL;
    omp_max_threads_fn omp = NULL;
    const char *fields[] = {
        "pid", "mapped_libraries", "mapped_library_count",
        "mkl_get_max_threads_available", "mkl_target_max_threads",
        "mkl_symbol_source", "query_kind",
        "omp_get_max_threads_available", "omp_target_max_threads",
        "omp_symbol_source"
    };
    (void)prhs;
    if (nrhs != 0 || nlhs > 1)
        mexErrMsgIdAndTxt("hgfx:perf01c:args", "Call with zero arguments and at most one output");

    paths[0] = '\0';
    sym_source[0] = '\0';
    omp_source[0] = '\0';
    omp = (omp_max_threads_fn)dlsym(RTLD_DEFAULT, "omp_get_max_threads");
    if (omp) {
        omp_found = 1;
        strncpy(omp_source, "RTLD_DEFAULT", sizeof(omp_source) - 1);
        omp_source[sizeof(omp_source) - 1] = '\0';
    }
    mk = (mkl_max_threads_fn)dlsym(RTLD_DEFAULT, "mkl_get_max_threads");
    if (!mk) mk = (mkl_max_threads_fn)dlsym(RTLD_DEFAULT, "MKL_Get_Max_Threads");
    if (mk) {
        symbol_found = 1;
        strncpy(sym_source, "RTLD_DEFAULT", sizeof(sym_source) - 1);
        sym_source[sizeof(sym_source) - 1] = '\0';
    }

    maps = fopen("/proc/self/maps", "r");
    if (!maps)
        mexErrMsgIdAndTxt("hgfx:perf01c:proc", "Cannot access /proc/self/maps for MATLAB process");

    while (fgets(line, sizeof(line), maps)) {
        char *path = strchr(line, '/');
        void *loaded = NULL;
        mkl_max_threads_fn candidate;
        if (!path || !matched_library(path)) continue;
        {
            char *end = strchr(path, '\n');
            if (end) *end = '\0';
            end = strstr(path, " (deleted)");
            if (end) *end = '\0';
        }
        if (!strstr(path, ".so")) continue;
        if (strstr(paths, path)) continue; /* no repeated map segments */
        if (strlen(paths) + strlen(path) + 2 >= sizeof(paths))
            mexErrMsgIdAndTxt("hgfx:perf01c:maps", "BLAS path list exceeds buffer");
        if (seen) strcat(paths, "\n");
        strcat(paths, path);
        seen++;

        /* Never load a new numerical library. Only query an already mapped .so */
        if (!symbol_found || !omp_found) {
            loaded = dlopen(path, RTLD_LAZY | RTLD_NOLOAD);
            if (loaded) {
                if (!symbol_found) {
                    candidate = (mkl_max_threads_fn)dlsym(loaded, "mkl_get_max_threads");
                    if (!candidate)
                        candidate = (mkl_max_threads_fn)dlsym(loaded, "MKL_Get_Max_Threads");
                    if (candidate) {
                        symbol_found = 1;
                        strncpy(sym_source, path, sizeof(sym_source) - 1);
                        sym_source[sizeof(sym_source) - 1] = '\0';
                        target = candidate();
                    }
                }
                if (!omp_found && (strstr(path, "iomp") || strstr(path, "gomp") ||
                                   strstr(path, "libomp"))) {
                    omp_max_threads_fn omp_candidate =
                        (omp_max_threads_fn)dlsym(loaded, "omp_get_max_threads");
                    if (omp_candidate) {
                        omp_found = 1;
                        strncpy(omp_source, path, sizeof(omp_source) - 1);
                        omp_source[sizeof(omp_source) - 1] = '\0';
                        omp_target = omp_candidate();
                    }
                }
                dlclose(loaded);
            }
        }
    }
    fclose(maps);

    if (mk && target < 0) target = mk();
    if (omp && omp_target < 0) omp_target = omp();
    plhs[0] = mxCreateStructMatrix(1, 1, 10, fields);
    mxSetField(plhs[0], 0, "pid", mxCreateDoubleScalar((double)getpid()));
    mxSetField(plhs[0], 0, "mapped_libraries", mxCreateString(paths));
    mxSetField(plhs[0], 0, "mapped_library_count", mxCreateDoubleScalar((double)seen));
    mxSetField(plhs[0], 0, "mkl_get_max_threads_available", mxCreateLogicalScalar(symbol_found != 0));
    mxSetField(plhs[0], 0, "mkl_target_max_threads", mxCreateDoubleScalar((double)target));
    mxSetField(plhs[0], 0, "mkl_symbol_source", mxCreateString(sym_source));
    mxSetField(plhs[0], 0, "omp_get_max_threads_available", mxCreateLogicalScalar(omp_found != 0));
    mxSetField(plhs[0], 0, "omp_target_max_threads", mxCreateDoubleScalar((double)omp_target));
    mxSetField(plhs[0], 0, "omp_symbol_source", mxCreateString(omp_source));
    mxSetField(plhs[0], 0, "query_kind",
               mxCreateString("TARGET_MAX_THREAD_CAP_NOT_OBSERVED_WORKER_COUNT"));
}
