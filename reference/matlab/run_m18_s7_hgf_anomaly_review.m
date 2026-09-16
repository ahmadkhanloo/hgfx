function run_m18_s7_hgf_anomaly_review(input_path, output_path)
%RUN_M18_S7_HGF_ANOMALY_REVIEW Exact-case MATLAB evidence for S7 review.
% Diagnostic only. It does not alter S7 seeds, data, starts or criteria.

root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root, 'external', 'hgf-toolbox')));
addpath(fullfile(root, 'reference', 'matlab', 'm11_shims'));

payload = jsondecode(fileread(input_path));
assert(strcmp(payload.protocol, 'm18-s7-hgf-anomaly-review-1'));
assert(strcmp(payload.parent_protocol, 'm18-s7-paired-recovery-1'));

out.protocol = payload.protocol;
out.parent_protocol = payload.parent_protocol;
out.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
out.matlab_version = version;
out.cases = cell(1, numel(payload.cases));

for k = 1:numel(payload.cases)
    c = payload.cases(k);
    y = double(c.y(:));
    u = double(c.u(:));

    pc = hgf_binary_config();
    oc = unitsq_sgm_config();
    fit = fitModel(y, u, pc, oc, 'quasinewton_optim_config');

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

    free_init = init(opt_idx)';
    matlab_final = fit.optim.final(opt_idx)';
    hgfx_final = double(c.current_hgfx.final_free(:)');
    copt = quasinewton_optim_config;
    baseline = quasinewton_optim(obj, free_init, copt);

    variants = cell(2*numel(free_init), 1);
    q = 0;
    for j = 1:numel(free_init)
        spacing = eps(free_init(j));
        for direction = [-1, 1]
            q = q + 1;
            start = free_init;
            start(j) = free_init(j) + direction*spacing;
            result = quasinewton_optim(obj, start, copt);
            item.label = sprintf('free_%d_%s_eps', j, ternary(direction < 0, 'minus', 'plus'));
            item.component_free_index_1based = j;
            item.component_full_index_1based = opt_idx(j);
            item.direction = direction;
            item.requested_spacing = spacing;
            item.actual_delta = start(j) - free_init(j);
            item.start = start;
            item.argMin = result.argMin;
            item.valMin = result.valMin;
            item.iter_rst = result.iter.rst;
            item.trace_last_finite_row = last_finite_row(result.iter.x);
            item.reset_count = numel(result.iter.rst);
            item.converged_inferred = item.trace_last_finite_row < 101 && item.reset_count < 10;
            variants{q} = item;
        end
    end
    variants = vertcat(variants{:});

    item.case_id = c.case_id;
    item.case_sha256 = c.case_sha256;
    item.seed = c.seed;
    item.trial_count = c.trial_count;
    item.truth_scale = c.truth_scale;
    item.replicate = c.replicate;
    item.free_full_indices_1based = opt_idx;
    item.free_init = free_init;
    item.official.final_free = matlab_final;
    item.official.negLj = fit.optim.negLj;
    item.official.trace_last_finite_row = last_finite_row(fit.optim.iter.x);
    item.official.reset_count = numel(fit.optim.iter.rst);
    item.official.converged_inferred = item.official.trace_last_finite_row < 101 && item.official.reset_count < 10;
    item.baseline.argMin = baseline.argMin;
    item.baseline.valMin = baseline.valMin;
    item.baseline.trace_last_finite_row = last_finite_row(baseline.iter.x);
    item.baseline.reset_count = numel(baseline.iter.rst);
    item.baseline.converged_inferred = item.baseline.trace_last_finite_row < 101 && item.baseline.reset_count < 10;
    item.objective_at_matlab_endpoint = obj(matlab_final);
    item.objective_at_hgfx_endpoint = obj(hgfx_final);
    item.variants = variants;
    out.cases{k} = item;

    fprintf('S7 HGF anomaly review %s baseline=%g variants=%d\n', char(c.case_id), baseline.valMin, numel(variants));
end

folder = fileparts(output_path);
if ~isempty(folder) && ~exist(folder, 'dir'); mkdir(folder); end
fid = fopen(output_path, 'w'); assert(fid >= 0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(hgfx_json_ieee(out), 'PrettyPrint', true));
end

function row = last_finite_row(x)
rows = find(any(isfinite(x), 2));
if isempty(rows); row = 0; else; row = rows(end); end
end

function out = ternary(cond, a, b)
if cond; out = a; else; out = b; end
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
