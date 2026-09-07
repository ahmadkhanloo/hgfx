function export_m5_ehgf_forward_parity(output_path)
%EXPORT_M5_EHGF_FORWARD_PARITY Export frozen HGF v8.2.0 eHGF trajectories.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

payload = struct;
payload.metadata.schema_version = 'm5-1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.matlab_version = version;
payload.metadata.numeric_mode = 'CPU float64';
payload.metadata.rng = 'deterministic/no RNG';
payload.metadata.optimizer = 'none';
payload.metadata.response_model = 'none';
payload.metadata.binary_forward = which('hgf_binary_unified');
payload.metadata.continuous_forward = which('hgf_unified');

args = {0.2, 0.05, 1.0, 0.2, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0};
[epi, emu, ev, ew] = hgf_volatility_update(args{:}, 'ehgf');
payload.safe_precision_case.ehgf = [epi, emu, ev, ew];

hgf_failed = false;
try
    hgf_volatility_update(args{:}, 'hgf');
catch ME
    hgf_failed = strcmp(ME.identifier, 'tapas:hgf:NegPostPrec');
end
payload.safe_precision_case.standard_hgf_rejects = hgf_failed;

binary_u = [0 1 1 0 1 0 1 1 0 0 1 1 1 0 1 0 0 1 1 0 1 0 1 1]';
binary_p = [NaN 0 1 NaN log(0.1) 0 NaN 0 0 0 0 NaN -3 2];
payload.trajectories.binary_regular = run_binary(binary_u, binary_p, false);

binary_dt = [0.5 1.0 1.5 0.8 1.2 0.7 1.1 0.9 1.3 1.0 0.6 1.4 1.0 0.75 1.25 0.8 1.1 0.9 1.2 0.7 1.3 0.85 1.15 0.95]';
binary_irr = [binary_u, binary_dt];
binary_irr(6,1) = NaN;
payload.trajectories.binary_irregular_ignored = run_binary(binary_irr, binary_p, true);

continuous_u = [0.20 0.25 0.18 0.30 0.22 0.27 0.24 0.31 0.29 0.20 0.19 0.23 0.26 0.28 0.30 0.25 0.21 0.18 0.20 0.24 0.27 0.29 0.26 0.22]';
continuous_p = [0.2 1.0 log(0.05) log(0.1) 0 0 0 -4 -6 log(100)];
payload.trajectories.continuous_regular = run_continuous(continuous_u, continuous_p, false);

continuous_dt = linspace(0.6, 1.4, length(continuous_u))';
continuous_irr = [continuous_u, continuous_dt];
continuous_irr(7,1) = NaN;
payload.trajectories.continuous_irregular_ignored = run_continuous(continuous_irr, continuous_p, true);

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m5:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M5 MATLAB eHGF forward export: PASS\n');
end

function out = run_binary(inputs, ptrans, irregular_intervals)
r = struct;
r.u = inputs;
r.ign = find(isnan(r.u(:,1)))';
r.c_prc = ehgf_binary_config;
r.c_prc.irregular_intervals = irregular_intervals;
r.c_prc.update_type = 'ehgf';
[traj, infStates] = hgf_binary_unified(r, ptrans, 'trans');
out = struct;
out.model = 'ehgf_binary';
out.inputs = inputs;
out.ptrans = ptrans;
out.irregular_intervals = irregular_intervals;
out.ignored_matlab_indices = r.ign;
out.traj = traj;
out.inf_states = infStates;
end

function out = run_continuous(inputs, ptrans, irregular_intervals)
r = struct;
r.u = inputs;
r.ign = find(isnan(r.u(:,1)))';
r.c_prc = ehgf_config;
r.c_prc.irregular_intervals = irregular_intervals;
r.c_prc.update_type = 'ehgf';
[traj, infStates] = hgf_unified(r, ptrans, 'trans');
out = struct;
out.model = 'ehgf';
out.inputs = inputs;
out.ptrans = ptrans;
out.irregular_intervals = irregular_intervals;
out.ignored_matlab_indices = r.ign;
out.traj = traj;
out.inf_states = infStates;
end
