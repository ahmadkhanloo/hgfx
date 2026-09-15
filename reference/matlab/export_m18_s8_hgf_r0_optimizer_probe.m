function export_m18_s8_hgf_r0_optimizer_probe(output_path)
%EXPORT_M18_S8_HGF_R0_OPTIMIZER_PROBE Frozen S8 localization for S7 HGF R0.
% Diagnostic only; it does not alter S7 acceptance or any scientific input.

root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root, 'external', 'hgf-toolbox')));
addpath(fullfile(root, 'reference', 'matlab', 'm11_shims'));

fixture_path = fullfile(root, 'reference', 'validation', 'm18_s7_paired_recovery', 'hgf_anomaly_fixture.json');
fixture = jsondecode(fileread(fixture_path));
case_id = 'PR-hgf_binary-T256-S0.35-R0';
expected_sha = '1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5';

selected = [];
for k = 1:numel(fixture.cases)
    if strcmp(fixture.cases(k).case_id, case_id)
        selected = fixture.cases(k);
        break
    end
end
assert(~isempty(selected), 'Frozen R0 case missing from fixture.');
assert(strcmp(selected.case_sha256, expected_sha), 'Frozen R0 case hash mismatch.');

u = double(selected.u(:));
y = double(selected.y(:));
fit = fitModel(y, u, hgf_binary_config(), unitsq_sgm_config(), 'quasinewton_optim_config');

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
nlj = @(p) workflow_nlj(r, r.c_prc.prc_fun, r.c_obs.obs_fun, ...
    p(1:n_prcpars), p(n_prcpars+1:n_prcpars+n_obspars));
obj = @(p_opt) workflow_restrict(nlj, init, opt_idx, p_opt);

trace = fit.optim.iter;
finite_rows = find(all(isfinite(trace.x), 2) & isfinite(trace.val));
assert(~isempty(finite_rows), 'No finite optimizer rows available.');

gradoptions.min_steps = 10;
probe.rows = finite_rows(:)';
probe.x = trace.x(finite_rows, :);
probe.val = trace.val(finite_rows);
probe.grad = NaN(numel(finite_rows), size(trace.x, 2));
probe.grad_err = NaN(numel(finite_rows), size(trace.x, 2));
probe.invH = cell(numel(finite_rows), 1);

for q = 1:numel(finite_rows)
    row = finite_rows(q);
    point = trace.x(row, :)';
    [g, e] = riddersgradient(obj, point, gradoptions);
    probe.grad(q, :) = g;
    probe.grad_err(q, :) = e;
    if row <= numel(trace.invH) && isfield(trace.invH(row), 'T') && ~isempty(trace.invH(row).T)
        probe.invH{q} = trace.invH(row).T;
    else
        probe.invH{q} = [];
    end
end

payload.protocol = 'm18-s8-hgf-r0-optimizer-probe-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.case_id = case_id;
payload.case_sha256 = expected_sha;
payload.seed = selected.seed;
payload.trial_count = selected.trial_count;
payload.truth_scale = selected.truth_scale;
payload.replicate = selected.replicate;
payload.free_indices_zero_based = selected.free_indices_zero_based;
payload.initial_free = fit.optim.init(opt_idx)';
payload.final_free = fit.optim.final(opt_idx)';
payload.negLj = fit.optim.negLj;
payload.trace.full_x = trace.x;
payload.trace.full_val = trace.val;
payload.trace.full_rst = trace.rst;
payload.trace.states = probe;

folder = fileparts(output_path);
if ~isempty(folder) && ~exist(folder, 'dir'); mkdir(folder); end
fid = fopen(output_path, 'w'); assert(fid >= 0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(hgfx_json_ieee(payload), 'PrettyPrint', true));
fprintf('M18 S8 HGF R0 optimizer probe: finite rows=%d final=%s\n', numel(finite_rows), mat2str(payload.final_free));
end

function val = workflow_restrict(f, arg, free_idx, free_arg)
arg(free_idx) = free_arg;
val = f(arg);
end

function negLogJoint = workflow_nlj(r, prc_fun, obs_fun, ptrans_prc, ptrans_obs)
try
    [~, infStates] = prc_fun(r, ptrans_prc, 'trans');
catch
    negLogJoint = realmax;
    return;
end
try
    [trialLogLls, ~, ~, ~] = obs_fun(r, infStates, ptrans_obs);
catch
    trialLogLls = obs_fun(r, infStates, ptrans_obs);
end
trialLogLls(r.irr) = [];
logLl = sum(trialLogLls);
if isnan(logLl)
    negLogJoint = realmax;
    return;
end
prc_idx = r.c_prc.priorsas;
prc_idx(isnan(prc_idx)) = 0;
prc_idx = find(prc_idx);
logPrcPriors = -1/2.*log(8*atan(1).*r.c_prc.priorsas(prc_idx)) ...
    - 1/2.*(ptrans_prc(prc_idx)-r.c_prc.priormus(prc_idx)).^2 ...
    ./r.c_prc.priorsas(prc_idx);
logPrcPrior = sum(logPrcPriors);
obs_idx = r.c_obs.priorsas;
obs_idx(isnan(obs_idx)) = 0;
obs_idx = find(obs_idx);
logObsPriors = -1/2.*log(8*atan(1).*r.c_obs.priorsas(obs_idx)) ...
    - 1/2.*(ptrans_obs(obs_idx)-r.c_obs.priormus(obs_idx)).^2 ...
    ./r.c_obs.priorsas(obs_idx);
logObsPrior = sum(logObsPriors);
negLogJoint = -(logLl + logPrcPrior + logObsPrior);
end
