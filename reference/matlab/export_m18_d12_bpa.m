function export_m18_d12_bpa(output_path)
% Frozen D12 Bayesian parameter averaging parity reference.
% The Python checker consumes the MATLAB fit estimates directly, isolating
% BPA algebra/trajectory parity from upstream optimizer parity.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

x = load(fullfile(root,'external','hgf-toolbox','demo','example_usdchf.txt'));
seed1 = 123;
seed2 = 456;
native1 = [1.04 1 .0001 .1 0 0 1 -13 -2 1e4];
native2 = [1.04 1 .0001 .1 0 0 1 -15 -2.5 1e4];
obs_native = .00002;

sim1 = simModel(x,'hgf',native1,'gaussian_obs',obs_native,seed1);
sim2 = simModel(x,'hgf',native2,'gaussian_obs',obs_native,seed2);
est1 = fitModel(sim1.y,x,'hgf_config','gaussian_obs_config','quasinewton_optim_config');
est2 = fitModel(sim2.y,x,'hgf_config','gaussian_obs_config','quasinewton_optim_config');
bpa = bayesian_parameter_average(est1,est2);

payload.protocol = 'm18-d12-bpa-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D12_bpa';
payload.seeds = [seed1 seed2];
payload.inputs = x;
payload.estimates = [compact_estimate(est1), compact_estimate(est2)];
payload.bpa.optim.H = bpa.optim.H;
payload.bpa.optim.Sigma = bpa.optim.Sigma;
payload.bpa.optim.Corr = bpa.optim.Corr;
payload.bpa.p_prc.p = bpa.p_prc.p;
payload.bpa.p_prc.ptrans = bpa.p_prc.ptrans;
payload.bpa.p_obs.p = bpa.p_obs.p;
payload.bpa.p_obs.ptrans = bpa.p_obs.ptrans;
payload.bpa.traj = bpa.traj;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D12 BPA reference exported.\n');
end

function out = compact_estimate(est)
out.u = est.u;
out.c_prc.model = est.c_prc.model;
out.c_prc.priormus = est.c_prc.priormus;
out.c_prc.priorsas = est.c_prc.priorsas;
out.c_obs.model = est.c_obs.model;
out.c_obs.priormus = est.c_obs.priormus;
out.c_obs.priorsas = est.c_obs.priorsas;
out.p_prc.ptrans = est.p_prc.ptrans;
out.p_obs.ptrans = est.p_obs.ptrans;
out.optim.H = est.optim.H;
end
