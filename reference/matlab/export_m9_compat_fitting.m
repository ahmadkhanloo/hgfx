function export_m9_compat_fitting(output_path)
%EXPORT_M9_COMPAT_FITTING Export optimizer and stable single-start MAP oracle.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

payload = struct;
payload.metadata.schema_version = 'm9-1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.optimizer = 'quasinewton_optim';
payload.metadata.numeric_mode = 'CPU float64';
payload.metadata.matlab_version = version;

c_opt = quasinewton_optim_config;
payload.optimizer_config = strip_config(c_opt);

quadfun = @(x) (x(1)-0.75).^2 + 2.*(x(2)+1.25).^2 + 0.15.*x(1).*x(2);
quad_init = [2; -3];
quad = quasinewton_optim(quadfun, quad_init, c_opt);
payload.quadratic.init = quad_init;
payload.quadratic.val_min = quad.valMin;
payload.quadratic.arg_min = quad.argMin;
payload.quadratic.inverse_hessian = quad.T;

u = [0 1 1 0 1 0 0 1 1 0 1 1 0 0 1 1 0 1 0 1 1 0 1 0]';
y = [0 1 1 0 1 0 0 1 0 0 1 1 0 1 1 0 0 1 0 1 1 0 1 0]';

r = make_r(y, u);
n_prc = length(r.c_prc.priormus);
n_obs = length(r.c_obs.priormus);

all_sas = [r.c_prc.priorsas, r.c_obs.priorsas];
idx_values = all_sas;
idx_values(isnan(idx_values)) = 0;
opt_idx = find(idx_values);

init = [r.c_prc.priormus, r.c_obs.priormus];
[init_nlj, init_negll, init_rval] = objective(r, init(1:n_prc), init(n_prc+1:n_prc+n_obs));
if init_rval ~= 0
    error('hgfx:m9:unstableInit', 'M9 fixture prior means are unstable.');
end

obj_free = @(p_opt) restricted_objective(p_opt, init, opt_idx, r, n_prc, n_obs);
fit = quasinewton_optim(obj_free, init(opt_idx)', c_opt);

final = init;
final(opt_idx) = fit.argMin';
[final_nlj, final_negll, final_rval] = objective( ...
    r, final(1:n_prc), final(n_prc+1:n_prc+n_obs));

[p_prc_native, ~] = hgf_binary_transp(r, final(1:n_prc));
[p_obs_native, ~] = unitsq_sgm_transp(r, final(n_prc+1:n_prc+n_obs));

payload.fit.inputs = u;
payload.fit.responses = y;
payload.fit.free_matlab_indices = opt_idx;
payload.fit.initial_full = init;
payload.fit.initial_free = init(opt_idx);
payload.fit.initial_neg_log_joint = init_nlj;
payload.fit.initial_neg_log_likelihood = init_negll;
payload.fit.arg_min = fit.argMin;
payload.fit.val_min = fit.valMin;
payload.fit.inverse_hessian = fit.T;
payload.fit.final_full = final;
payload.fit.perceptual_transformed = final(1:n_prc);
payload.fit.observation_transformed = final(n_prc+1:n_prc+n_obs);
payload.fit.perceptual_native = p_prc_native;
payload.fit.observation_native = p_obs_native;
payload.fit.neg_log_joint = final_nlj;
payload.fit.neg_log_likelihood = final_negll;
payload.fit.rval = final_rval;

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m9:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M9 MATLAB compatibility fitting export: PASS\n');
end

function c = strip_config(copt)
c = struct;
c.tolGrad = copt.tolGrad;
c.tolArg = copt.tolArg;
c.maxStep = copt.maxStep;
c.maxIter = copt.maxIter;
c.maxRegu = copt.maxRegu;
c.maxRst = copt.maxRst;
c.nRandInit = copt.nRandInit;
c.seedRandInit = copt.seedRandInit;
c.optIter = copt.optIter;
end

function r = make_r(responses, inputs)
r = struct;
r.y = responses;
r.u = inputs;
r.ign = find(isnan(r.u(:,1)))';
response_irr = find(isnan(r.y(:,1)))';
r.irr = unique([r.ign, response_irr]);
r.c_prc = hgf_binary_config;
r.c_obs = unitsq_sgm_config;
end

function value = restricted_objective(p_opt, init, opt_idx, r, n_prc, n_obs)
full = init;
full(opt_idx) = p_opt;
value = objective(r, full(1:n_prc), full(n_prc+1:n_prc+n_obs));
end

function [negLogJoint, negLogLl, rval] = objective(r, ptrans_prc, ptrans_obs)
try
    [~, infStates] = hgf_binary_unified(r, ptrans_prc, 'trans');
catch
    negLogJoint = realmax;
    negLogLl = realmax;
    rval = -1;
    return;
end

trialLogLls = unitsq_sgm(r, infStates, ptrans_obs);
trialLogLls(r.irr) = [];
logLl = sum(trialLogLls);
if isnan(logLl)
    negLogLl = realmax;
else
    negLogLl = -logLl;
end

prc_idx_values = r.c_prc.priorsas;
prc_idx_values(isnan(prc_idx_values)) = 0;
prc_idx = find(prc_idx_values);
logPrcPriors = -1/2 .* log(8*atan(1) .* r.c_prc.priorsas(prc_idx)) ...
    -1/2 .* (ptrans_prc(prc_idx)-r.c_prc.priormus(prc_idx)).^2 ...
    ./ r.c_prc.priorsas(prc_idx);

obs_idx_values = r.c_obs.priorsas;
obs_idx_values(isnan(obs_idx_values)) = 0;
obs_idx = find(obs_idx_values);
logObsPriors = -1/2 .* log(8*atan(1) .* r.c_obs.priorsas(obs_idx)) ...
    -1/2 .* (ptrans_obs(obs_idx)-r.c_obs.priormus(obs_idx)).^2 ...
    ./ r.c_obs.priorsas(obs_idx);

negLogJoint = -(logLl + sum(logPrcPriors) + sum(logObsPriors));
rval = 0;
end
