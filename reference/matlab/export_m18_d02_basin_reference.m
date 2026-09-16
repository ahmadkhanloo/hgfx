function export_m18_d02_basin_reference(output_path)
% Frozen classification-only D02 cross-endpoint diagnostic reference.
% See docs/validation/M18_D02_BASIN_DIAGNOSTIC.md.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

u = load(fullfile(root,'external','hgf-toolbox','demo','example_binary_input.txt'));
seed = 123456789;
native = [NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3];

sim = simModel(u,'ehgf_binary',native,'unitsq_sgm',5,seed);
pc = ehgf_binary_config;
oc = unitsq_sgm_config;
oc.logzesa = .5;
oc = align_priors(oc);
fit = fitModel(sim.y,u,pc,oc,'quasinewton_optim_config');

payload.metadata.protocol = 'm18-d02-basin-probe-1';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.numeric_encoding = 'ieee-strings-v1';
payload.metadata.matlab_version = version;
payload.metadata.policy = 'docs/validation/M18_D02_BASIN_DIAGNOSTIC.md';
payload.case_id = 'D02_fit';
payload.seed = seed;
payload.inputs = u;
payload.responses = sim.y;
payload.obs_prior_variance = .5;
payload.prc_priormus = fit.c_prc.priormus;
payload.prc_priorsas = fit.c_prc.priorsas;
payload.obs_priormus = fit.c_obs.priormus;
payload.obs_priorsas = fit.c_obs.priorsas;
payload.matlab_final = fit.optim.final;
payload.matlab_negLj = fit.optim.negLj;
payload.n_prcpars = length(fit.c_prc.priormus);
payload.n_obspars = length(fit.c_obs.priormus);

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D02 basin reference exported: negLj=%.17g\n',fit.optim.negLj);
end