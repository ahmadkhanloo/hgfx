function export_m18_d08_source_likelihood_probe(output_path)
% Frozen likelihood localization for the first D08 holdout source residual.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

u = load(fullfile(root,'external','hgf-toolbox','demo','example_usdchf.txt'));
seed = 314159265;
native = [1.04 1 .0001 .1 0 0 1 -13 -2 1e4];
obs_native = .00002;
s = simModel(u,'uhgf',native,'gaussian_obs',obs_native,seed);
pc = uhgf_config;
oc = gaussian_obs_config;
fit = fitModel(s.y,u,pc,oc,'quasinewton_optim_config');

r.u = fit.u; r.y = fit.y; r.irr = fit.irr; r.ign = fit.ign;
r.c_prc = fit.c_prc; r.c_obs = fit.c_obs;
init = fit.optim.init;
opt_mask = [r.c_prc.priorsas, r.c_obs.priorsas];
opt_mask(isnan(opt_mask)) = 0;
opt_idx = find(opt_mask);
n_prcpars = length(r.c_prc.priormus);
n_obspars = length(r.c_obs.priormus);

source_row = 38;
component_1based = 1;
ridders_step_1based = 1;
h = 1.0;
source_x = fit.optim.iter.x(source_row,:)';
sample_free = source_x;
sample_free(component_1based) = source_x(component_1based) + h;
full = init;
full(opt_idx) = sample_free;
ptrans_prc = full(1:n_prcpars);
ptrans_obs = full(n_prcpars+1:n_prcpars+n_obspars);
[~,infStates] = r.c_prc.prc_fun(r,ptrans_prc,'trans');
[logp,yhat,res] = r.c_obs.obs_fun(r,infStates,ptrans_obs);

regular_logp = logp;
regular_logp(r.irr) = [];
log_likelihood_sum = sum(regular_logp);
log_likelihood_scalar_loop = 0;
for k = 1:numel(regular_logp)
    log_likelihood_scalar_loop = log_likelihood_scalar_loop + regular_logp(k);
end

x = infStates(:,1,1);
x_regular = x;
x_regular(r.irr) = [];
y_regular = r.y(:,1);
y_regular(r.irr) = [];
ze = exp(ptrans_obs(1));
normalizer = -1/2.*log(8*atan(1).*ze);
residual = y_regular-x_regular;
squared_residual = residual.^2;
denominator = 2.*ze;
quadratic = squared_residual./denominator;
logp_formula = normalizer-quadratic;

payload.protocol = 'm18-d08-source-likelihood-probe-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D08_fit';
payload.seed = seed;
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
payload.ptrans_prc = ptrans_prc;
payload.ptrans_obs = ptrans_obs;
payload.inf_states = infStates;
payload.observation_x = x;
payload.ze = ze;
payload.trial_log_likelihoods = logp;
payload.log_likelihood_sum = log_likelihood_sum;
payload.log_likelihood_scalar_loop = log_likelihood_scalar_loop;
payload.yhat = yhat;
payload.res = res;
payload.regular_y = y_regular;
payload.primitives.normalizer = normalizer;
payload.primitives.residual = residual;
payload.primitives.squared_residual = squared_residual;
payload.primitives.denominator = denominator;
payload.primitives.quadratic = quadratic;
payload.primitives.logp_formula = logp_formula;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D08 source likelihood probe exported: row=%d component=%d step=%d side=%s\n',source_row,component_1based,ridders_step_1based,payload.side);
end
