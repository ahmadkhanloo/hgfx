function export_m18_s8_hgf_r0_negative_precision_probe(output_path)
%EXPORT_M18_S8_HGF_R0_NEGATIVE_PRECISION_PROBE
% Diagnostic-only localization of the frozen MATLAB HGF negative-posterior-
% precision boundary at the three immutable R0 Ridders plus points.
%
% This file does not modify toolbox code or acceptance criteria. It mirrors the
% standard three-level hgf_binary recurrence with the same frozen MATLAB
% primitives and records the scalar operands immediately before the source
% would raise tapas:hgf:NegPostPrec.

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
assert(isempty(fit.ign));
assert(isempty(fit.irr));

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
center = fit.optim.iter.x(10,:)';

steps = [2 4 5];
div = 1.2;
points = repmat(struct(), numel(steps), 1);
for q = 1:numel(steps)
    step = steps(q);
    h = 1/(div^(step-1));
    free = center;
    free(1) = free(1) + h;
    full = init;
    full(opt_idx) = free;
    p_prc = full(1:n_prcpars);

    point = probe_point(r, p_prc);
    point.step_1based = step;
    point.h = h;
    point.side = 'plus';
    point.free = free;
    points(q) = point;
end

payload.protocol = 'm18-s8-hgf-r0-negative-precision-probe-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.case_id = case_id;
payload.case_sha256 = case_sha;
payload.matlab_optimizer_row_1based = 10;
payload.free_component_1based = 1;
payload.points = points;
payload.note = ['Diagnostic only. The three points are the immutable MATLAB-invalid ', ...
    'Ridders plus points from S8. The recurrence mirrors frozen hgf_binary.m ', ...
    'through the pi_3 <= 0 guard and records its operands; no product code, ', ...
    'scientific input, threshold, start, optimizer, or release criterion changes.'];

folder = fileparts(output_path);
if ~isempty(folder) && ~exist(folder, 'dir'); mkdir(folder); end
fid = fopen(output_path, 'w'); assert(fid >= 0);
cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid, '%s\n', jsonencode(hgfx_json_ieee(payload), 'PrettyPrint', true));
fprintf('M18 S8 R0 negative-precision probe: failures=%d/%d\n', sum([points.negative_precision]), numel(points));
end

function point = probe_point(r, ptrans)
p = hgf_binary_transp(r, ptrans);
p = double(p(:)');
l = r.c_prc.n_levels;
assert(l == 3);

mu_0 = p(1:l);
sa_0 = p(l+1:2*l);
rho  = p(2*l+1:3*l);
ka   = p(3*l+1:4*l-1);
om   = p(4*l:5*l-2);
th   = exp(p(5*l-1));

u = [0; r.u(:,1)];
n = length(u);
t = ones(n,1);

mu = NaN(n,l);
pi = NaN(n,l);
muhat = NaN(n,l);
pihat = NaN(n,l);
v = NaN(n,l);
w = NaN(n,l-1);
da = NaN(n,l);

mu(1,1) = tapas_sgm(mu_0(1), 1);
pi(1,1) = Inf;
mu(1,2:end) = mu_0(2:end);
pi(1,2:end) = 1./sa_0(2:end);

history.trial_1based = NaN(n-1,1);
history.pihat2 = NaN(n-1,1);
history.pi2 = NaN(n-1,1);
history.da2 = NaN(n-1,1);
history.mu3_prev = NaN(n-1,1);
history.pi3_prev = NaN(n-1,1);
history.muhat3 = NaN(n-1,1);
history.pihat3 = NaN(n-1,1);
history.exp_arg2 = NaN(n-1,1);
history.exp2 = NaN(n-1,1);
history.v2 = NaN(n-1,1);
history.w2 = NaN(n-1,1);
history.pi3_candidate = NaN(n-1,1);
history.mu3 = NaN(n-1,1);
history.da3 = NaN(n-1,1);

negative_precision = false;
failure_trial = NaN;
filled = 0;
for k = 2:n
    assert(~ismember(k-1, r.ign));

    muhat(k,2) = mu(k-1,2) + t(k)*rho(2);
    muhat(k,1) = tapas_sgm(ka(1)*muhat(k,2), 1);
    pihat(k,1) = 1/(muhat(k,1)*(1-muhat(k,1)));
    pi(k,1) = Inf;
    mu(k,1) = u(k);
    da(k,1) = mu(k,1) - muhat(k,1);

    pihat(k,2) = 1/(1/pi(k-1,2) + exp(ka(2)*mu(k-1,3) + om(2)));
    pi(k,2) = pihat(k,2) + ka(1)^2/pihat(k,1);
    mu(k,2) = muhat(k,2) + ka(1)/pi(k,2)*da(k,1);
    da(k,2) = (1/pi(k,2) + (mu(k,2)-muhat(k,2))^2)*pihat(k,2) - 1;

    muhat(k,3) = mu(k-1,3) + t(k)*rho(3);
    pihat(k,3) = 1/(1/pi(k-1,3) + t(k)*th);
    v(k,3) = t(k)*th;
    exp_arg2 = ka(2)*mu(k-1,3) + om(2);
    exp2 = exp(exp_arg2);
    v(k,2) = t(k)*exp2;
    w(k,2) = v(k,2)*pihat(k,2);
    pi_candidate = pihat(k,3) + 1/2*ka(2)^2*w(k,2)*(w(k,2) + (2*w(k,2)-1)*da(k,2));

    filled = filled + 1;
    history.trial_1based(filled) = k-1;
    history.pihat2(filled) = pihat(k,2);
    history.pi2(filled) = pi(k,2);
    history.da2(filled) = da(k,2);
    history.mu3_prev(filled) = mu(k-1,3);
    history.pi3_prev(filled) = pi(k-1,3);
    history.muhat3(filled) = muhat(k,3);
    history.pihat3(filled) = pihat(k,3);
    history.exp_arg2(filled) = exp_arg2;
    history.exp2(filled) = exp2;
    history.v2(filled) = v(k,2);
    history.w2(filled) = w(k,2);
    history.pi3_candidate(filled) = pi_candidate;

    pi(k,3) = pi_candidate;
    if pi(k,3) <= 0
        negative_precision = true;
        failure_trial = k-1;
        break
    end

    mu(k,3) = muhat(k,3) + 1/2*1/pi(k,3)*ka(2)*w(k,2)*da(k,2);
    da(k,3) = (1/pi(k,3) + (mu(k,3)-muhat(k,3))^2)*pihat(k,3) - 1;
    history.mu3(filled) = mu(k,3);
    history.da3(filled) = da(k,3);
end

names = fieldnames(history);
for i = 1:numel(names)
    history.(names{i}) = history.(names{i})(1:filled,:);
end

point.negative_precision = negative_precision;
point.failure_trial_1based = failure_trial;
point.native_parameters = p;
point.theta = th;
point.ka2 = ka(2);
point.om2 = om(2);
point.history = history;
if negative_precision
    point.failure.pihat2 = history.pihat2(end);
    point.failure.pi2 = history.pi2(end);
    point.failure.da2 = history.da2(end);
    point.failure.mu3_prev = history.mu3_prev(end);
    point.failure.pi3_prev = history.pi3_prev(end);
    point.failure.muhat3 = history.muhat3(end);
    point.failure.pihat3 = history.pihat3(end);
    point.failure.exp_arg2 = history.exp_arg2(end);
    point.failure.exp2 = history.exp2(end);
    point.failure.v2 = history.v2(end);
    point.failure.w2 = history.w2(end);
    point.failure.pi3_candidate = history.pi3_candidate(end);
else
    point.failure = struct();
end
end
