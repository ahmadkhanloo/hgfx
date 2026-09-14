function export_m18_s8_hgf_r0_ridders_stencil(output_path)
%EXPORT_M18_S8_HGF_R0_RIDDERS_STENCIL Exact Ridders stencil evidence for S8 R0.

root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root, 'external', 'hgf-toolbox')));
addpath(fullfile(root, 'reference', 'matlab', 'm11_shims'));

fixture = jsondecode(fileread(fullfile(root, 'reference', 'validation', 'm18_s7_paired_recovery', 'hgf_anomaly_fixture.json')));
case_id = 'PR-hgf_binary-T256-S0.35-R0';
case_sha = '1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5';
selected = [];
for k = 1:numel(fixture.cases)
    if strcmp(fixture.cases(k).case_id, case_id)
        selected = fixture.cases(k);
        break
    end
end
assert(~isempty(selected));
assert(strcmp(selected.case_sha256, case_sha));

u = double(selected.u(:));
y = double(selected.y(:));
fit = fitModel(y, u, hgf_binary_config(), unitsq_sgm_config(), 'quasinewton_optim_config');
assert(all(isfinite(fit.optim.iter.x(10,:))));

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
assert(isequal(opt_idx(:)', [13 14 15]));

n_prcpars = length(r.c_prc.priormus);
n_obspars = length(r.c_obs.priormus);
center = fit.optim.iter.x(10,:)';
component = 1;

init_h = 1;
div = 1.2;
min_steps = 10;
max_steps = 100;
tf = 2;
P = NaN(max_steps);
err = realmax;
df = NaN;
h = init_h;
samples = cell(max_steps,1);

for i = 1:max_steps
    if i > 1
        h = h/div;
    end
    plus = center;
    minus = center;
    plus(component) = center(component) + h;
    minus(component) = center(component) - h;
    ep = evaluate_free(r, init, opt_idx, plus, n_prcpars, n_obspars);
    em = evaluate_free(r, init, opt_idx, minus, n_prcpars, n_obspars);
    P(i,1) = (ep.neg_joint-em.neg_joint)/(2*h);
    if i > 1
        divsq = div^2;
        t = divsq;
        for j = 2:i
            P(i,j) = (t*P(i,j-1)-P(i-1,j-1))/(t-1);
            t = t*divsq;
            currerr = max(abs(P(i,j)-P(i,j-1)), abs(P(i,j)-P(i-1,j-1)));
            if currerr < err
                err = currerr;
                df = P(i,j);
            end
        end
    end
    item.step_1based = i;
    item.h = h;
    item.plus = ep;
    item.minus = em;
    item.base_derivative = P(i,1);
    item.best_derivative = df;
    item.best_error = err;
    samples{i} = item;

    if i > min_steps && abs(P(i,i)-P(i-1,i-1)) > tf*err
        samples = samples(1:i);
        break
    end
end

payload.protocol = 'm18-s8-hgf-r0-ridders-stencil-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.case_id = case_id;
payload.case_sha256 = case_sha;
payload.matlab_optimizer_row_1based = 10;
payload.free_component_1based = component;
payload.center = center;
payload.reference_gradient = fit.optim.iter.x(10,:); % provenance for row identity only
payload.ridders_gradient = df;
payload.ridders_error = err;
payload.options.init_h = init_h;
payload.options.div = div;
payload.options.min_steps = min_steps;
payload.options.max_steps = max_steps;
payload.options.tf = tf;
payload.samples = vertcat(samples{:});

folder = fileparts(output_path);
if ~isempty(folder) && ~exist(folder, 'dir'); mkdir(folder); end
fid = fopen(output_path, 'w'); assert(fid >= 0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(hgfx_json_ieee(payload), 'PrettyPrint', true));
fprintf('M18 S8 R0 Ridders stencil: steps=%d derivative=%.17g error=%.17g\n', numel(payload.samples), df, err);
end

function e = evaluate_free(r, init, opt_idx, free, n_prcpars, n_obspars)
full = init;
full(opt_idx) = free;
p_prc = full(1:n_prcpars);
p_obs = full(n_prcpars+1:n_prcpars+n_obspars);
try
    [~, infStates] = r.c_prc.prc_fun(r, p_prc, 'trans');
catch
    e.neg_joint = realmax;
    e.neg_log_likelihood = realmax;
    e.prc_prior = NaN;
    e.obs_prior = NaN;
    e.trial_log_likelihoods = NaN(size(r.y));
    e.inf_states = NaN;
    e.free = free;
    return
end
try
    [trialLogLls, ~, ~, ~] = r.c_obs.obs_fun(r, infStates, p_obs);
catch
    trialLogLls = r.c_obs.obs_fun(r, infStates, p_obs);
end
trial_for_sum = trialLogLls;
trial_for_sum(r.irr) = [];
logLl = sum(trial_for_sum);
prc_idx = r.c_prc.priorsas;
prc_idx(isnan(prc_idx)) = 0;
prc_idx = find(prc_idx);
logPrcPriors = -1/2.*log(8*atan(1).*r.c_prc.priorsas(prc_idx)) ...
    - 1/2.*(p_prc(prc_idx)-r.c_prc.priormus(prc_idx)).^2 ./ r.c_prc.priorsas(prc_idx);
logPrcPrior = sum(logPrcPriors);
obs_idx = r.c_obs.priorsas;
obs_idx(isnan(obs_idx)) = 0;
obs_idx = find(obs_idx);
logObsPriors = -1/2.*log(8*atan(1).*r.c_obs.priorsas(obs_idx)) ...
    - 1/2.*(p_obs(obs_idx)-r.c_obs.priormus(obs_idx)).^2 ./ r.c_obs.priorsas(obs_idx);
logObsPrior = sum(logObsPriors);
e.free = free;
e.neg_joint = -(logLl + logPrcPrior + logObsPrior);
e.neg_log_likelihood = -logLl;
e.prc_prior = logPrcPrior;
e.obs_prior = logObsPrior;
e.trial_log_likelihoods = trialLogLls;
e.inf_states = infStates;
end
