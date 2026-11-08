/*
 * PERF-01C read-only MATLAB in-process BLAS/MKL inspection MEX.
 * Diagnostic ONLY: no timers, BLAS replacement, or thread-setting API.
 * mkl_get_max_threads gives TARGET max threads, NOT active workers.
 *
 * Uses RTLD_NOLOAD: no new BLAS libraries can be initialized by this probe.
 * Preserve original frozen MATLAB source; compile probe outside repository.
 */
#define _GNU_SOURCE
#include "mex.h"
#include <ctype.h>
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define MAPS_BUF_SIZE 524288
#define PATH_LIMIT 4096
typedef int (*mkl_max_threads_fn)(void);

static int matched_library(const char *src) {
    char lower[PATH_LIMIT];
    size_t n = strlen(src);
    size_t i;
    if (n >= sizeof(lower)) n = sizeof(lower) - 1;
    for (i = 0; i < n; ++i) lower[i] = (char)tolower((unsigned char)src[i]);
    lower[n] = '\0';
    return (strstr(lower, "mkl") || strstr(lower, "blas") ||
            strstr(lower, "blis") || strstr(lower, "aocl") ||
            strstr(lower, "omp") || strstr(lower, "iomp")) != NULL;
}

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]) {
    FILE *maps;
    char line[8192];
    char paths[MAPS_BUF_SIZE];
    char sym_source[PATH_LIMIT];
    int target = -1, symbol_found = 0, seen = 0;
    mkl_max_threads_fn mk = NULL;
    const char *fields[] = {
        "pid", "mapped_libraries", "mapped_library_count",
        "mkl_get_max_threads_available", "mkl_target_max_threads",
        "mkl_symbol_source", "query_kind"
    };
    (void)prhs;
    if (nrhs != 0 || nlhs > 1)
        mexErrMsgIdAndTxt("hgfx:perf01c:args", "Call with zero arguments and at most one output");

    paths[0] = '\0';
    sym_source[0] = '\0';
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
        if (!mk) {
            loaded = dlopen(path, RTLD_LAZY | RTLD_NOLOAD);
            if (loaded) {
                candidate = (mkl_max_threads_fn)dlsym(loaded, "mkl_get_max_threads");
                if (!candidate)
                    candidate = (mkl_max_threads_fn)dlsym(loaded, "MKL_Get_Max_Threads");
                if (candidate) {
                    mk = candidate;
                    symbol_found = 1;
                    strncpy(sym_source, path, sizeof(sym_source) - 1);
                    sym_source[sizeof(sym_source) - 1] = '\0';
                    /* Keep existing library handle reference until after call. */
                    target = mk();
                }
                dlclose(loaded);
                if (symbol_found) mk = NULL; /* target was read while handle live */
            }
        }
    }
    fclose(maps);

    if (mk && target < 0) target = mk();
    plhs[0] = mxCreateStructMatrix(1, 1, 7, fields);
    mxSetField(plhs[0], 0, "pid", mxCreateDoubleScalar((double)getpid()));
    mxSetField(plhs[0], 0, "mapped_libraries", mxCreateString(paths));
    mxSetField(plhs[0], 0, "mapped_library_count", mxCreateDoubleScalar((double)seen));
    mxSetField(plhs[0], 0, "mkl_get_max_threads_available", mxCreateLogicalScalar(symbol_found != 0));
    mxSetField(plhs[0], 0, "mkl_target_max_threads", mxCreateDoubleScalar((double)target));
    mxSetField(plhs[0], 0, "mkl_symbol_source", mxCreateString(sym_source));
    mxSetField(plhs[0], 0, "query_kind",
               mxCreateString("TARGET_MAX_THREAD_CAP_NOT_OBSERVED_WORKER_COUNT"));
}
