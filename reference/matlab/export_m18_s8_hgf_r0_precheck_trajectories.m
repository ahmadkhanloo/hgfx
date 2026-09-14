function export_m18_s8_hgf_r0_precheck_trajectories(output_path)
%EXPORT_M18_S8_HGF_R0_PRECHECK_TRAJECTORIES Raw MATLAB HGF states before validity checking.
% Diagnostic-only: shadows hgf_check_trajectories with a temporary no-op after
% the official fit is complete, so the frozen hgf_binary implementation can be
% observed immediately before its final validity gate. The toolbox source is
% not modified.

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
center = fit.optim.iter.x(10,:)';

% Shadow only the terminal validity checker. Keep all perceptual update code,
% transforms, and primitive functions from the frozen toolbox untouched.
shim_dir = tempname;
mkdir(shim_dir);
shim_file = fullfile(shim_dir, 'hgf_check_trajectories.m');
fid = fopen(shim_file, 'w'); assert(fid >= 0);
fprintf(fid, 'function hgf_check_trajectories(varargin)\n');
fprintf(fid, '%% Diagnostic no-op: raw states before the frozen terminal validity gate.\n');
fprintf(fid, 'end\n');
fclose(fid);
addpath(shim_dir, '-begin');
cleanup = onCleanup(@() cleanup_shim(shim_dir)); %#ok<NASGU>
clear hgf_check_trajectories hgf_binary hgf_binary_unified

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

    [traj, ~] = r.c_prc.prc_fun(r, p_prc, 'trans');
    pi = 1./traj.sa;
    pihat = 1./traj.sahat;
    dmu = diff(traj.mu(:,2:end));
    dpi = diff(pi(:,2:end));
    rmdmu = sqrt(mean(dmu.^2));
    rmdpi = sqrt(mean(dpi.^2));
    ratio_mu = abs(dmu)./repmat(rmdmu, size(dmu,1), 1);
    ratio_pi = abs(dpi)./repmat(rmdpi, size(dpi,1), 1);
    [max_mu_ratio, idx_mu] = max(ratio_mu(:));
    [max_pi_ratio, idx_pi] = max(ratio_pi(:));
    [mu_row, mu_col] = ind2sub(size(ratio_mu), idx_mu);
    [pi_row, pi_col] = ind2sub(size(ratio_pi), idx_pi);

    item.step_1based = step;
    item.h = h;
    item.side = 'plus';
    item.free = free;
    item.invalid_by_formula = any(ratio_mu(:) > 16) || any(ratio_pi(:) > 16);
    item.rmdmu = rmdmu;
    item.rmdpi = rmdpi;
    item.max_mu_ratio = max_mu_ratio;
    item.max_pi_ratio = max_pi_ratio;
    item.max_mu_ratio_index_1based = [mu_row mu_col];
    item.max_pi_ratio_index_1based = [pi_row pi_col];
    item.mu = traj.mu;
    item.pi = pi;
    item.muhat = traj.muhat;
    item.pihat = pihat;
    item.v = traj.v;
    item.w = traj.w;
    item.da = traj.da;
    item.psi = traj.psi;
    item.epsi = traj.epsi;
    points(q) = item;
end

payload.protocol = 'm18-s8-hgf-r0-precheck-trajectory-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.case_id = case_id;
payload.case_sha256 = case_sha;
payload.matlab_optimizer_row_1based = 10;
payload.free_component_1based = 1;
payload.jump_tol = 16;
payload.points = points;
payload.note = 'Diagnostic only. Frozen toolbox source is unchanged; a temporary no-op shadows only the terminal hgf_check_trajectories call after the official fit, exposing raw pre-check states for the three immutable MATLAB-invalid Ridders plus points.';

folder = fileparts(output_path);
if ~isempty(folder) && ~exist(folder, 'dir'); mkdir(folder); end
fid = fopen(output_path, 'w'); assert(fid >= 0);
file_cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid, '%s\n', jsonencode(hgfx_json_ieee(payload), 'PrettyPrint', true));
fprintf('M18 S8 R0 precheck trajectories: points=%d invalid=%d\n', numel(points), sum([points.invalid_by_formula]));
end

function cleanup_shim(shim_dir)
try
    rmpath(shim_dir);
catch
end
clear hgf_check_trajectories hgf_binary hgf_binary_unified
try
    rmdir(shim_dir, 's');
catch
end
end
