function run_m18_s7_paired_recovery_shard(input_path, output_path)
%RUN_M18_S7_PAIRED_RECOVERY_SHARD Evaluate one frozen S7 shard in MATLAB.
%
% The input u/y arrays are generated once by the Python case preparer and are
% consumed unchanged here. This runner never simulates/resamples cases.

root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root, 'external', 'hgf-toolbox')));

payload = jsondecode(fileread(input_path));
assert(strcmp(payload.protocol, 'm18-s7-paired-recovery-1'));

out = struct();
out.protocol = payload.protocol;
out.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
out.matlab_version = version;
out.shard = payload.shard;
out.input_shard_sha256 = payload.shard_sha256;
out.parameter_results = cell(1, numel(payload.parameter_cases));
out.model_results = cell(1, numel(payload.model_cases));

for k = 1:numel(payload.parameter_cases)
    c = payload.parameter_cases(k);
    r = fit_one(char(c.model), double(c.y(:)), double(c.u(:)));
    r.case_id = c.case_id;
    r.case_sha256 = c.case_sha256;
    r.truth_free = double(c.truth_free(:)');
    r.seed = c.seed;
    r.replicate = c.replicate;
    out.parameter_results{k} = r;
    fprintf('S7 MATLAB parameter %s success=%d\n', c.case_id, r.success);
end

candidates = {'hgf_binary','ehgf_binary','uhgf_binary'};
for k = 1:numel(payload.model_cases)
    c = payload.model_cases(k);
    mr = struct();
    mr.case_id = c.case_id;
    mr.case_sha256 = c.case_sha256;
    mr.generating_model = char(c.generating_model);
    mr.seed = c.seed;
    mr.replicate = c.replicate;
    mr.candidates = cell(1, numel(candidates));
    bics = inf(1, numel(candidates));
    for j = 1:numel(candidates)
        fr = fit_one(candidates{j}, double(c.y(:)), double(c.u(:)));
        mr.candidates{j} = fr;
        if fr.success && isfinite(fr.BIC)
            bics(j) = fr.BIC;
        end
    end
    [best_bic, idx] = min(bics);
    if isfinite(best_bic)
        mr.selected_model = candidates{idx};
        mr.selection_success = true;
    else
        mr.selected_model = '';
        mr.selection_success = false;
    end
    mr.bic_vector = bics;
    out.model_results{k} = mr;
    fprintf('S7 MATLAB model %s selected=%s\n', c.case_id, mr.selected_model);
end

folder = fileparts(output_path);
if ~isempty(folder) && ~exist(folder, 'dir'); mkdir(folder); end
fid = fopen(output_path, 'w');
assert(fid >= 0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(hgfx_json_ieee(out), 'PrettyPrint', true));
end

function out = fit_one(model, y, u)
out = struct();
out.model = model;
out.success = false;
out.error_identifier = '';
out.error_message = '';
out.final_free = [];
out.initial_free = [];
out.free_indices_zero_based = [];
out.negLj = NaN;
out.negLl = NaN;
out.AIC = NaN;
out.BIC = NaN;
out.LME = NaN;
out.trace_last_finite_row = 0;
out.reset_count = 0;
out.converged_inferred = false;

try
    pc = feval([model '_config']);
    oc = unitsq_sgm_config();
    fit = fitModel(y, u, pc, oc, 'quasinewton_optim_config');

    mask = [fit.c_prc.priorsas, fit.c_obs.priorsas];
    mask(isnan(mask)) = 0;
    opt_idx = find(mask);

    out.final_free = fit.optim.final(opt_idx);
    out.initial_free = fit.optim.init(opt_idx);
    out.free_indices_zero_based = opt_idx - 1;
    out.negLj = fit.optim.negLj;
    out.negLl = fit.optim.negLl;
    out.AIC = fit.optim.AIC;
    out.BIC = fit.optim.BIC;
    out.LME = fit.optim.LME;

    % The frozen MATLAB optimizer prints rather than returns its termination
    % reason. Infer convergence conservatively from the frozen optIter trace:
    % exhausting all 100 iterations or all 10 resets is non-converged.
    if isstruct(fit.optim.iter) && isfield(fit.optim.iter, 'x')
        finite_rows = find(any(isfinite(fit.optim.iter.x), 2));
        if ~isempty(finite_rows); out.trace_last_finite_row = finite_rows(end); end
        if isfield(fit.optim.iter, 'rst'); out.reset_count = numel(fit.optim.iter.rst); end
        out.converged_inferred = out.trace_last_finite_row < 101 && out.reset_count < 10;
    end
    out.success = true;
catch ME
    out.error_identifier = ME.identifier;
    out.error_message = ME.message;
end
end
