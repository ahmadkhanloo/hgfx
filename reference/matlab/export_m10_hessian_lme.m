function export_m10_hessian_lme(output_path)
%EXPORT_M10_HESSIAN_LME Export full fit statistics and restart-selection oracle.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

payload = struct;
payload.metadata.schema_version = 'm10-1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.numeric_mode = 'CPU float64';
payload.metadata.matlab_version = version;

u = [0 1 1 0 1 0 0 1 1 0 1 1 0 0 1 1 0 1 0 1 1 0 1 0]';
y = [0 1 1 0 1 0 0 1 0 0 1 1 0 1 1 0 0 1 0 1 1 0 1 0]';

est = fitModel(y, u, 'hgf_binary_config', 'unitsq_sgm_config', 'quasinewton_optim_config');
payload.fit.inputs = u;
payload.fit.responses = y;
payload.fit.final = est.optim.final;
payload.fit.H = est.optim.H;
payload.fit.Sigma = est.optim.Sigma;
payload.fit.Corr = est.optim.Corr;
payload.fit.negLl = est.optim.negLl;
payload.fit.negLj = est.optim.negLj;
payload.fit.LME = est.optim.LME;
payload.fit.decompLME = est.optim.decompLME;
payload.fit.accu = est.optim.accu;
payload.fit.comp = est.optim.comp;
payload.fit.AIC = est.optim.AIC;
payload.fit.BIC = est.optim.BIC;

% Explicit formula oracle for the optimizer-T fallback branch.
H_bad = [1 0; 0 -0.25];
T = [0.5 0.02; 0.02 0.25];
H_fb = nearest_psd(inv(T));
Sigma_fb = nearest_psd(T);
Corr_fb = tapas_Cov2Corr(Sigma_fb);
d = 2;
valMin = 5;
negLl = 4;
LME = -valMin + 1/2*log(1/det(H_fb)) + d/2*log(2*pi);
payload.fallback.H = H_fb;
payload.fallback.Sigma = Sigma_fb;
payload.fallback.Corr = Corr_fb;
payload.fallback.LME = LME;
payload.fallback.logjoint = -valMin;
payload.fallback.postpredcorr = 1/2*log(1/det(H_fb));
payload.fallback.freepars = d/2*log(2*pi);
payload.fallback.accu = -negLl;
payload.fallback.comp = -negLl-LME;
payload.fallback.AIC = 2*negLl+2*d;
payload.fallback.BIC = 2*negLl+d*log(20);

% Seeded MATLAB starts are exported explicitly. Python validates LME-based
% selection from these same starts, not MATLAB-vs-NumPy RNG identity.
c_prc = hgf_binary_config;
c_obs = unitsq_sgm_config;
all_sas = [c_prc.priorsas, c_obs.priorsas];
idx_values = all_sas;
idx_values(isnan(idx_values)) = 0;
opt_idx = find(idx_values);
base = [c_prc.priormus, c_obs.priormus];
optsds = sqrt(all_sas(opt_idx));

seed = 314159;
nRandInit = 2;
rng(seed);
starts = NaN(nRandInit, length(opt_idx));
for i = 1:nRandInit
    draw = base;
    draw(opt_idx) = draw(opt_idx) + randn(1,length(optsds)).*optsds;
    starts(i,:) = draw(opt_idx);
end

c_opt = quasinewton_optim_config;
c_opt.nRandInit = nRandInit;
c_opt.seedRandInit = seed;
est_multi = fitModel(y, u, c_prc, c_obs, c_opt);

payload.multistart.seed = seed;
payload.multistart.nRandInit = nRandInit;
payload.multistart.restart_free_parameters = starts;
payload.multistart.final = est_multi.optim.final;
payload.multistart.LME = est_multi.optim.LME;
payload.multistart.negLj = est_multi.optim.negLj;
payload.multistart.H = est_multi.optim.H;
payload.multistart.Sigma = est_multi.optim.Sigma;
payload.multistart.Corr = est_multi.optim.Corr;
payload.multistart.AIC = est_multi.optim.AIC;
payload.multistart.BIC = est_multi.optim.BIC;

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m10:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M10 MATLAB Hessian/LME export: PASS\n');
end
