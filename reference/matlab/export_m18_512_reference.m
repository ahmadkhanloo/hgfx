function export_m18_512_reference(input_path, output_path)
%EXPORT_M18_512_REFERENCE Compare the frozen 512-trial M18B cell against MATLAB HGF 8.2.0.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

case_payload = jsondecode(fileread(input_path));
expected_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
if ~strcmp(case_payload.reference.commit, expected_commit)
    error('hgfx:m18_512:referenceMismatch', 'Unexpected frozen reference commit.');
end
if case_payload.historical_cell.trial_count ~= 512 || case_payload.historical_cell.seed ~= 233100
    error('hgfx:m18_512:caseMismatch', 'Unexpected historical cell; expected 512 trials and seed 233100.');
end

u = double(case_payload.inputs(:));
y = double(case_payload.responses(:));
truth_prc = double(case_payload.truth_perceptual_transformed(:))';
default_prc = double(case_payload.default_perceptual_transformed(:))';
default_obs = double(case_payload.default_observation_transformed(:))';

r = struct;
r.u = u;
r.y = y;
r.ign = find(isnan(r.u(:,1)))';
response_irr = find(isnan(r.y(:,1)))';
r.irr = unique([r.ign, response_irr]);
r.c_prc = hgf_binary_config;
r.c_obs = unitsq_sgm_config;

payload = struct;
payload.metadata.schema_version = 'm18-512-1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = expected_commit;
payload.metadata.matlab_version = version;
payload.metadata.numeric_mode = 'CPU float64';
payload.metadata.case_seed = 233100;
payload.metadata.trial_count = 512;
payload.metadata.model = 'hgf_binary';
payload.metadata.observation_model = 'unitsq_sgm';

payload.truth_forward = run_forward(r, truth_prc);
payload.default_forward = run_forward(r, default_prc);
payload.initial_objective = run_objective(r, default_prc, default_obs);
payload.fit = run_fit(r, default_prc, default_obs);

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m18_512:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M18 512-trial MATLAB reference export: COMPLETE\n');
end

function out = run_forward(r, ptrans_prc)
out = struct;
try
    [traj, infStates] = hgf_binary_unified(r, ptrans_prc, 'trans');
    out.success = true;
    out.error_identifier = '';
    out.error_message = '';
    out.traj = traj;
    out.inf_states = infStates;
    out.all_finite = all_struct_finite(traj) && all(isfinite(infStates(:)) | isnan(infStates(:)));
catch ME
    out.success = false;
    out.error_identifier = ME.identifier;
    out.error_message = ME.message;
    out.traj = struct;
    out.inf_states = [];
    out.all_finite = false;
end
end

function out = run_objective(r, ptrans_prc, ptrans_obs)
out = struct;
try
    [~, infStates] = hgf_binary_unified(r, ptrans_prc, 'trans');
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

    out.neg_log_likelihood = negLogLl;
    out.neg_log_joint = -(logLl + sum(logPrcPriors) + sum(logObsPriors));
    out.rval = 0;
    out.success = isfinite(out.neg_log_joint) && isfinite(out.neg_log_likelihood);
    out.error_identifier = '';
    out.error_message = '';
catch ME
    out.neg_log_likelihood = realmax;
    out.neg_log_joint = realmax;
    out.rval = -1;
    out.success = false;
    out.error_identifier = ME.identifier;
    out.error_message = ME.message;
end
end

function out = run_fit(r, default_prc, default_obs)
out = struct;
initial = run_objective(r, default_prc, default_obs);
if ~initial.success || initial.rval ~= 0
    out.attempted = false;
    out.success = false;
    out.reason = 'initial_objective_unstable';
    out.error_identifier = initial.error_identifier;
    out.error_message = initial.error_message;
    return;
end
try
    n_prc = length(default_prc);
    n_obs = length(default_obs);
    full = [default_prc, default_obs];
    all_sas = [r.c_prc.priorsas, r.c_obs.priorsas];
    idx_values = all_sas;
    idx_values(isnan(idx_values)) = 0;
    opt_idx = find(idx_values);

    c_opt = quasinewton_optim_config;
    c_opt.nRandInit = 0;
    c_opt.maxIter = 100;
    obj_free = @(p_opt) restricted_objective(p_opt, full, opt_idx, r, n_prc, n_obs);
    fit = quasinewton_optim(obj_free, full(opt_idx)', c_opt);
    final = full;
    final(opt_idx) = fit.argMin';
    final_obj = run_objective(r, final(1:n_prc), final(n_prc+1:n_prc+n_obs));

    out.attempted = true;
    out.success = final_obj.success;
    out.reason = '';
    out.error_identifier = '';
    out.error_message = '';
    out.arg_min = fit.argMin;
    out.val_min = fit.valMin;
    out.final_full = final;
    out.final_neg_log_joint = final_obj.neg_log_joint;
    out.final_neg_log_likelihood = final_obj.neg_log_likelihood;
catch ME
    out.attempted = true;
    out.success = false;
    out.reason = 'optimizer_or_final_objective_error';
    out.error_identifier = ME.identifier;
    out.error_message = ME.message;
end
end

function value = restricted_objective(p_opt, init, opt_idx, r, n_prc, n_obs)
full = init;
full(opt_idx) = p_opt;
obj = run_objective(r, full(1:n_prc), full(n_prc+1:n_prc+n_obs));
value = obj.neg_log_joint;
end

function result = all_struct_finite(s)
result = true;
fields = fieldnames(s);
for i = 1:numel(fields)
    value = s.(fields{i});
    if isnumeric(value)
        if any(~isfinite(value(:)) & ~isnan(value(:)))
            result = false;
            return;
        end
    end
end
end
