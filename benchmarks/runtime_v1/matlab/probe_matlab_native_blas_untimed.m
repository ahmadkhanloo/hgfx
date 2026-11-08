function probe_matlab_native_blas_untimed(output_path, source_file)
% PERF-01C only: discover MATLAB-loaded BLAS libraries and MKL max-thread
% target from within the MATLAB process. Not a benchmark or worker-counter.
% The source MEX uses RTLD_NOLOAD: it cannot initialize another BLAS.
r = struct();
r.schema = 'perf01c-matlab-native-blas-untimed-v1';
r.status = 'READ_ONLY_NATIVE_LIBRARY_DIAGNOSTIC_NOT_BENCHMARK';
r.clock = 'ABSENT';
r.performance = 'NOT_MEASURED';
r.scientific_gate = 'BLOCK_FREEZE_NOT_FROZEN';
r.github_run_id = getenv('GITHUB_RUN_ID');
r.github_sha = getenv('GITHUB_SHA');
r.matlab_release = version('-release');
r.process_pid = double(matlabProcessID());
r.boot_id = strtrim(fileread('/proc/sys/kernel/random/boot_id'));
r.requested_mkl_env_inside_matlab = getenv('MKL_NUM_THREADS');
r.max_num_comp_threads = maxNumCompThreads;
r.blas_workload = 'A*transpose(A) numeric library discovery; NOT HGFX input';
r.blas_workload_diagnostics = 'no clock and no repeated benchmark';
r.thread_count_before = proc_threads(r.process_pid);

% Deliberately no random seed or model/data mutation: a small untimed
% matrix product causes the actual installed MATLAB BLAS implementation to
% be initialized before /proc mappings and native API are consulted.
A = reshape(double(1:(128*128)),128,128);
B = A * A';
if ~isfinite(B(1,1))
    error('hgfx:perf01c:native','BLAS discovery computation not finite');
end
r.thread_count_after_blas = proc_threads(r.process_pid);
r.native_mkl_api_compile_status = 'NOT_COMPILED';
r.native_mkl_api_error_identifier = '';
r.native_mkl_api_error_message = '';
r.native = struct();
try
    [folder,~,~] = fileparts(output_path);
    build_dir = fullfile(folder, 'mex_build');
    if ~isfolder(build_dir), mkdir(build_dir); end
    mex('-silent','-outdir',build_dir,source_file);
    addpath(build_dir);
    r.native_mkl_api_compile_status = 'COMPILED';
    r.native = perf01c_native_mkl_probe();
    if r.native.pid ~= r.process_pid
        error('hgfx:perf01c:pid','Native MEX introspected wrong process');
    end
catch ME
    % Instrumentation unavailability is NOT an environment pass; archive the
    % actual failure and permit a strict comparator to classify it.
    r.native_mkl_api_compile_status = 'UNAVAILABLE_OR_FAILED';
    r.native_mkl_api_error_identifier = ME.identifier;
    r.native_mkl_api_error_message = ME.message;
end
r.active_blas_worker_count_proven = false;
r.unmodified_environment_rule_satisfied = ~isempty(r.requested_mkl_env_inside_matlab) && ...
    strcmp(r.requested_mkl_env_inside_matlab,'1');
r.thread_count_after_probe = proc_threads(r.process_pid);
[folder,~,~] = fileparts(output_path);
if ~isempty(folder) && ~isfolder(folder), mkdir(folder); end
fid = fopen(output_path,'w');
if fid < 0, error('hgfx:perf01c:output','Cannot write native evidence'); end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(r));
fprintf('MATLAB native BLAS inspection exported; actual worker count remains unknown; no timer\n');
end

function num = proc_threads(pid)
status = fileread(sprintf('/proc/%d/status',pid));
tokens = regexp(status,'(?m)^Threads:[ \t]*(\d+)','tokens','once');
if isempty(tokens)
    error('hgfx:perf01c:threads','No thread-count field in /proc status');
end
num = str2double(tokens{1});
end
