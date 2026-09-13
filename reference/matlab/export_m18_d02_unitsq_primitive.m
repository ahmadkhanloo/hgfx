function export_m18_d02_unitsq_primitive(output_path)
% Diagnostic-only D02 unit-square likelihood primitive probe.
% Targets the largest remaining per-trial likelihood mismatch in the frozen
% exact-coordinate decomposition after the MATLAB-compatible exp repair.
% No acceptance threshold, seed, dataset, start point, optimizer, or model changes.
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

r.u = fit.u;
r.y = fit.y;
r.irr = fit.irr;
r.ign = fit.ign;
r.c_prc = fit.c_prc;
r.c_obs = fit.c_obs;

init = fit.optim.init;
opt_mask = [r.c_prc.priorsas, r.c_obs.priorsas];
opt_mask(isnan(opt_mask)) = 0;
opt_idx = find(opt_mask);
n_prcpars = length(r.c_prc.priormus);
n_obspars = length(r.c_obs.priormus);

trace = fit.optim.iter;
finite_rows = find(all(isfinite(trace.x),2) & isfinite(trace.val));
x0 = trace.x(finite_rows(1),:)';

% Parameter 2, first Ridders minus sample: h=1.
% The preceding exact-coordinate decomposition identified trial 83 (1-based)
% as the largest remaining per-trial likelihood mismatch at this sample.
sample_free = x0;
sample_free(2) = x0(2) - 1;

full = init;
full(opt_idx) = sample_free;
ptrans_prc = full(1:n_prcpars);
ptrans_obs = full(n_prcpars+1:n_prcpars+n_obspars);

[~,infStates] = r.c_prc.prc_fun(r,ptrans_prc,'trans');
[logp,yhat,res] = r.c_obs.obs_fun(r,infStates,ptrans_obs);

pop = 1;
if r.c_obs.predorpost == 2
    pop = 3;
end
observation_x = infStates(:,1,pop);
ze = exp(ptrans_obs(1));

x = observation_x;
x(r.irr) = [];
y = r.y(:,1);
y(r.irr) = [];

logx_raw = log(x);
log1pxm1 = log1p(x-1);
use_log1pxm1 = (1-x)<1e-4;
logx_used = logx_raw;
logx_used(use_log1pxm1) = log1pxm1(use_log1pxm1);

log1mx_raw = log(1-x);
log1pmx = log1p(-x);
use_log1pmx = x<1e-4;
log1mx_used = log1mx_raw;
log1mx_used(use_log1pmx) = log1pmx(use_log1pmx);

pow1mx = (1-x).^ze;
powx = x.^ze;
denom = pow1mx + powx;
logdenom = log(denom);
term1 = y.*ze.*(logx_used-log1mx_used);
term2 = ze.*log1mx_used;
logp_formula = term1 + term2 - logdenom;

payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.protocol = 'm18-d02-unitsq-primitive-1';
payload.case_id = 'D02_fit';
payload.sample = 'parameter_2_first_ridders_minus';
payload.trial_focus_1based = 83;
payload.inputs = u;
payload.responses = sim.y;
payload.obs_prior_variance = .5;
payload.initial_free = x0;
payload.sample_free = sample_free;
payload.full_transformed = full;
payload.inf_states = infStates;
payload.observation_x = observation_x;
payload.ze = ze;
payload.trial_log_likelihoods = logp;
payload.yhat = yhat;
payload.res = res;
payload.regular_y = y;
payload.primitives.logx_raw = logx_raw;
payload.primitives.log1pxm1 = log1pxm1;
payload.primitives.use_log1pxm1 = double(use_log1pxm1);
payload.primitives.logx_used = logx_used;
payload.primitives.log1mx_raw = log1mx_raw;
payload.primitives.log1pmx = log1pmx;
payload.primitives.use_log1pmx = double(use_log1pmx);
payload.primitives.log1mx_used = log1mx_used;
payload.primitives.pow1mx = pow1mx;
payload.primitives.powx = powx;
payload.primitives.denom = denom;
payload.primitives.logdenom = logdenom;
payload.primitives.term1 = term1;
payload.primitives.term2 = term2;
payload.primitives.logp_formula = logp_formula;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w');
assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));

fprintf('M18 D02 unitsq primitive: sample=%s trial=%d\n', ...
    payload.sample,payload.trial_focus_1based);
end
