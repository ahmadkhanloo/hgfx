function export_m18_demo_uhgf_ar1_reference(output_path)
%EXPORT_M18_DEMO_UHGF_AR1_REFERENCE Freeze the official uHGF -> AR(1) demo workflow.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

expected_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
u = load(fullfile(hgf_root, 'demo', 'example_binary_input.txt'));

% Exact native-space vectors from frozen demo/hgf_demo.m.
p_uhgf = [NaN 0 1 NaN 1 1 NaN 0 0 1 1 NaN -2.5 3];
p_ar1 = [NaN 0 1 NaN 1 1 NaN 0 0.3 NaN 0 1 NaN 0 0 1 1 NaN -2.5 3];

payload = struct;
payload.metadata.schema_version = 'm18-demo-uhgf-ar1-2';
payload.metadata.numeric_encoding = 'ieee-strings-v1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = expected_commit;
payload.metadata.matlab_version = version;
payload.metadata.demo_source = 'demo/hgf_demo.m';
payload.metadata.demo_input = 'demo/example_binary_input.txt';
payload.metadata.case_id = 'D04_UHGF_TO_AR1_WORKFLOW';
payload.inputs = u;
payload.uhgf_native_parameters = p_uhgf;
payload.uhgf_ar1_native_parameters = p_ar1;
payload.uhgf_binary = run_uhgf(u, p_uhgf);
payload.uhgf_ar1_binary = run_ar1(u, p_ar1);

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m18demoar1:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(hgfx_json_ieee(payload), 'PrettyPrint', true));
fprintf('HGFX M18 uHGF->AR1 MATLAB reference export: COMPLETE\n');
end

function out = run_uhgf(u, p)
r = base_r(u);
r.c_prc = uhgf_binary_config;
out = capture(@() uhgf_binary(r,p));
end

function out = run_ar1(u, p)
r = base_r(u);
r.c_prc = uhgf_ar1_binary_config;
out = capture(@() uhgf_ar1_binary(r,p));
end

function r = base_r(u)
r = struct;
r.u = u;
r.ign = find(isnan(r.u(:,1)))';
end

function out = capture(fn)
out = struct;
try
    [traj, infStates] = fn();
    out.success = true;
    out.error_identifier = '';
    out.error_message = '';
    out.traj = traj;
    out.inf_states = infStates;
    if isfield(traj,'mu')
        mu = traj.mu;
        out.max_abs_mu_all = max(abs(mu(:)), [], 'omitnan');
        if size(mu,2) >= 3
            out.max_abs_mu_level3 = max(abs(mu(:,3)), [], 'omitnan');
        else
            out.max_abs_mu_level3 = NaN;
        end
    else
        out.max_abs_mu_all = NaN;
        out.max_abs_mu_level3 = NaN;
    end
catch ME
    out.success = false;
    out.error_identifier = ME.identifier;
    out.error_message = ME.message;
    out.traj = struct;
    out.inf_states = [];
    out.max_abs_mu_all = NaN;
    out.max_abs_mu_level3 = NaN;
end
end
