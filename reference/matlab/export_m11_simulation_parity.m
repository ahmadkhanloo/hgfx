function export_m11_simulation_parity(output_path)
%EXPORT_M11_SIMULATION_PARITY Export simulation/sampling oracle for HGFX M11.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));
addpath(fullfile(repo_root, 'reference', 'matlab', 'm11_shims'));

payload = struct;
payload.metadata.schema_version = 'm11-1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.numeric_mode = 'CPU float64';
payload.metadata.matlab_version = version;
payload.metadata.rng_contract = 'same-runtime seeded reproducibility; cross-runtime random drivers exported explicitly';

% -------------------------------------------------------------------------
% simModel: fixed native parameters, response probability, ignored semantics
% -------------------------------------------------------------------------
u = [0 1 1 NaN 0 1 0 1 1 0 1 0]';
p_prc = [NaN 0 1 NaN .1 1 NaN 0 0 1 1 NaN -2.7 -5.4];
p_obs = 12;
seed = 271828;

sim = simModel(u, 'hgf_binary', p_prc, 'unitsq_sgm', p_obs, seed);
payload.sim.inputs = u;
payload.sim.seed = seed;
payload.sim.ignored_matlab = sim.ign;
payload.sim.p_prc = sim.p_prc.p;
payload.sim.p_obs = sim.p_obs.p;
payload.sim.responses = sim.y;
payload.sim.probability = sim.yhat;
payload.sim.traj.mu = sim.traj.mu;
payload.sim.traj.sa = sim.traj.sa;
payload.sim.traj.muhat = sim.traj.muhat;
payload.sim.traj.sahat = sim.traj.sahat;
payload.sim.traj.da = sim.traj.da;

% Recompute full infStates because simModel intentionally does not expose it.
r = struct;
r.u = u;
r.ign = find(isnan(u(:,1)))';
r.c_prc = hgf_binary_config;
[traj_full, infStates] = hgf_binary(r, p_prc);
payload.sim.infStates = infStates;
payload.sim.full_muhat = traj_full.muhat;
payload.sim.full_sahat = traj_full.sahat;

% Export deterministic Bernoulli drivers. They validate sampling semantics
% without claiming MATLAB and NumPy have identical RNG streams.
uniforms = linspace(.03,.97,length(u))';
payload.sim.exported_uniforms = uniforms;
payload.sim.exported_uniform_responses = double(uniforms < sim.yhat);

% -------------------------------------------------------------------------
% sampleModel: prior sampling + transforms + trajectories + obs parameters
% -------------------------------------------------------------------------
us = [0 1 1 0 1 0 0 1 1 0 1 0 0 1 1 0]';
c_prc = hgf_binary_config;
c_prc.omsa = [NaN .01 .01];
c_prc = align_priors(c_prc);
c_obs = unitsq_sgm_config;
seed_sample = 314159;

rng(seed_sample);
z_prc = randn(1,length(c_prc.priorsas));
z_obs = randn(1,length(c_obs.priorsas));

sam = sampleModel(us, c_prc, c_obs, seed_sample);
payload.sample.inputs = us;
payload.sample.seed = seed_sample;
payload.sample.prc_standard_normals = z_prc;
payload.sample.obs_standard_normals = z_obs;
payload.sample.p_prc_trans = sam.p_prc.ptrans;
payload.sample.p_prc = sam.p_prc.p;
payload.sample.p_obs_trans = sam.p_obs.ptrans;
payload.sample.p_obs = sam.p_obs.p;
payload.sample.traj.mu = sam.traj.mu;
payload.sample.traj.sa = sam.traj.sa;
payload.sample.traj.muhat = sam.traj.muhat;
payload.sample.traj.sahat = sam.traj.sahat;
payload.sample.traj.da = sam.traj.da;

% sampleModel's observation function resets the RNG to c_sim.seed. The
% resulting y is exported only as evidence, not for cross-runtime equality.
payload.sample.responses = sam.y;

outdir = fileparts(output_path);
if ~isempty(outdir) && ~exist(outdir,'dir')
    mkdir(outdir);
end
fid = fopen(output_path,'w');
if fid == -1
    error('hgfx:m11:openFailed','Could not open %s',output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(payload,'PrettyPrint',true));
fprintf('HGFX M11 MATLAB simulation export: PASS\n');
end
