function export_m18_d02_source_likelihood_probe(output_path)
% Frozen diagnostic-only likelihood localization for the first D02 source-probe residual.
% See docs/validation/M18_D02_SOURCE_LIKELIHOOD_DIAGNOSTIC.md.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

u = load(fullfile(root,'external','hgf-toolbox','demo','example_binary_input.txt'));
seed = 123456789;
native = [NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3];
s = simModel(u,'ehgf_binary',native,'unitsq_sgm',5,seed);
pc = ehgf_binary_config;
oc = unitsq_sgm_config;
oc.logzesa = .5;
oc = align_priors(oc);
fit = fitModel(s.y,u,pc,oc,'quasinewton_optim_config');

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

source_row = 7;
component_1based = 1;
ridders_step_1based = 2;
h = 1/(1.2^(ridders_step_1based-1));
source_x = fit.optim.iter.x(source_row,:)';
sample_free = source_x;
sample_free(component_1based) = source_x(component_1based) + h;

full = init;
full(opt_idx) = sample_free;
ptrans_prc = full(1:n_prcpars);
ptrans_obs = full(n_prcpars+1:n_prcpars+n_obspars);
[~,infStates] = r.c_prc.prc_fun(r,ptrans_prc,'trans');
[logp,yhat,res] = r.c_obs.obs_fun(r,infStates,ptrans_obs);

logp_regular = logp;
logp_regular(r.irr) = [];
log_likelihood_sum = sum(logp_regular);
log_likelihood_scalar_loop = 0;
for k = 1:numel(logp_regular)
    log_likelihood_scalar_loop = log_likelihood_scalar_loop + logp_regular(k);
end

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

payload.protocol = 'm18-d02-source-likelihood-probe-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D02_fit';
payload.seed = seed;
payload.obs_prior_variance = .5;
payload.source_trace_row_1based = source_row;
payload.component_free_index_1based = component_1based;
payload.component_full_index_1based = opt_idx(component_1based);
payload.ridders_step_1based = ridders_step_1based;
payload.side = 'plus';
payload.h = h;
payload.inputs = u;
payload.responses = s.y;
payload.source_x = source_x;
payload.sample_free = sample_free;
payload.full_transformed = full;
payload.inf_states = infStates;
payload.observation_x = observation_x;
payload.ze = ze;
payload.trial_log_likelihoods = logp;
payload.log_likelihood_sum = log_likelihood_sum;
payload.log_likelihood_scalar_loop = log_likelihood_scalar_loop;
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
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D02 source likelihood probe exported: row=%d component=%d step=%d side=%s\n', ...
    source_row,component_1based,ridders_step_1based,payload.side);
end
