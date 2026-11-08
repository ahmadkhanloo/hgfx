function probe_cpu_host_matlab_untimed(output_path)
% PERF-01C: inspect same physical CI host and MATLAB thread request, NO TIMER.
% This does not prove active MATLAB BLAS/MKL thread equivalence.
maxNumCompThreads(1);
current_threads = maxNumCompThreads;
if current_threads ~= 1
    error('hgfx:perf01c:threads','MATLAB CPU thread request not honored');
end
r = struct();
r.schema = 'perf01c-cpu-host-untimed-matlab-v1';
r.status = 'AUTHOR_SIDE_HOST_DIAGNOSTIC_ONLY_NO_TIMING';
r.engine = 'matlab';
r.source_sha = '2437f4dc241541072722a2695ddeca7b44d83dd3';
r.github_run_id = getenv('GITHUB_RUN_ID');
r.github_sha = getenv('GITHUB_SHA');
r.boot_id = strtrim(fileread('/proc/sys/kernel/random/boot_id'));
r.kernel_release = shell_output('uname -r');
r.os_arch = shell_output('uname -m');
cpuinfo = fileread('/proc/cpuinfo');
r.cpu_model = cpuinfo_field(cpuinfo,'model name');
r.cpu_vendor = cpuinfo_field(cpuinfo,'vendor_id');
r.cpu_microcode = cpuinfo_field(cpuinfo,'microcode');
r.cpu_flags = cpuinfo_field(cpuinfo,'flags');
r.online_logical_cpus = str2double(shell_output('nproc --all'));
status = fileread('/proc/self/status');
m = regexp(status,'(?m)^Cpus_allowed_list:[ \t]*([^\r\n]+)','tokens','once');
if isempty(m)
    error('hgfx:perf01c:affinity','MATLAB /proc/self/status lacks affinity');
end
r.allowed_cpu_list = strtrim(m{1});
vars = {'OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',...
    'BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'};
env_requests = struct();
for i = 1:numel(vars)
    env_requests.(vars{i}) = getenv(vars{i});
end
r.environment_thread_requests = env_requests;
r.matlab_max_num_comp_threads = current_threads;
r.matlab_version = version;
r.matlab_release = version('-release');
r.matlab_platform = computer;
r.matlab_blas_runtime = 'NOT_INDEPENDENTLY_OBSERVED';
gpath = '/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor';
if isfile(gpath)
    r.cpu_frequency_governor = strtrim(fileread(gpath));
else
    r.cpu_frequency_governor = 'NOT_VISIBLE';
end
r.timers = 'ABSENT';
r.scientific_gate = 'BLOCK_FREEZE_NOT_FROZEN';
[folder,~,~] = fileparts(output_path);
if ~isempty(folder) && ~isfolder(folder), mkdir(folder); end
fid = fopen(output_path,'w');
if fid < 0
    error('hgfx:perf01c:io','Could not write MATLAB host attestation');
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(r));
fprintf('MATLAB host, affinity and requested threads recorded; BLAS runtime unverified; no timing\n');
end

function value = cpuinfo_field(txt,key)
expr = ['(?m)^',regexptranslate('escape',key),'[ \t]*:[ \t]*([^\r\n]+)'];
found = regexp(txt,expr,'tokens','once');
if isempty(found)
    error('hgfx:perf01c:cpuinfo','Missing /proc/cpuinfo field: %s',key);
end
value = strtrim(found{1});
end

function value = shell_output(cmd)
[status,value] = system(cmd);
if status ~= 0
    error('hgfx:perf01c:shell','Host metadata command failed: %s',cmd);
end
value = strtrim(value);
end
