function matlab_reference_preflight(inputs_dir, toolbox_dir, output_path)
%MATLAB_REFERENCE_PREFLIGHT Exact frozen-oracle fixed-vector preflight.
% No timing, fitting, changes to data, or scientific PASS claims.

expected_sha = '2437f4dc241541072722a2695ddeca7b44d83dd3';
if ~isfolder(inputs_dir) || ~isfolder(toolbox_dir)
    error('hgfx:perf01:paths', 'Input data or reference toolbox folder not found.');
end
addpath(genpath(toolbox_dir));
if isempty(which('fitModel')) || isempty(which('hgf_binary_unified'))
    error('hgfx:perf01:reference', 'Frozen MATLAB HGF toolbox functions missing.');
end
manifest = jsondecode(fileread(fullfile(inputs_dir, 'inputs_manifest.json')));
if ~strcmp(manifest.matlab_oracle_sha, expected_sha)
    error('hgfx:perf01:reference', 'Frozen oracle SHA mismatch in manifest.');
end

report = struct();
report.schema = 'hgfx-runtime-matlab-reference-preflight-v1';
report.status = 'MATLAB_FIXED_VECTOR_PREFLIGHT_NOT_PERFORMANCE_NOT_FINAL_PARITY';
report.matlab_release = version('-release');
report.matlab_version = version();
report.oracle_expected_sha = expected_sha;
report.fitModel_path = which('fitModel');
report.hgf_binary_unified_path = which('hgf_binary_unified');
report.input_manifest_identity = manifest.protocol_id;
report.cells = struct('model', {}, 'n_trials', {}, 'case_id', {}, ...
    'status', {}, 'error_identifier', {}, 'error_message', {}, ...
    'start_matches_matlab_priors', {}, 'neg_log_joint', {}, ...
    'neg_log_likelihood', {}, 'trial_log_likelihood_count', {});

models = {'hgf_binary', 'ehgf_binary', 'uhgf_binary'};
horizons = [128, 512, 1024];
for hi = 1:numel(horizons)
    n = horizons(hi);
    data = jsondecode(fileread(fullfile(inputs_dir, 'inputs', ...
        sprintf('binary_%d_s64.json', n))));
    if size(data.u, 1) ~= 64 || size(data.u, 2) ~= n
        error('hgfx:perf01:inputs', 'Unexpected input dimensions for n=%d.', n);
    end
    u = double(data.u(1,:))';
    y = double(data.y(1,:))';
    for mi = 1:numel(models)
        model = models{mi};
        item = struct();
        item.model = model;
        item.n_trials = n;
        item.case_id = sprintf('%s_%d', model, n);
        item.status = 'MATLAB_NOT_RUN';
        item.error_identifier = '';
        item.error_message = '';
        item.start_matches_matlab_priors = false;
        item.neg_log_joint = [];
        item.neg_log_likelihood = [];
        item.trial_log_likelihood_count = 0;
        try
            snap = jsondecode(fileread(fullfile(inputs_dir, 'configs', ...
                sprintf('%s_%d.json', model, n))));
            p = decode_numeric_records(snap.transformed_start_full);
            c_prc = feval([model '_config']);
            c_obs = unitsq_sgm_config();
            n_prc = numel(c_prc.priormus);
            n_obs = numel(c_obs.priormus);
            if numel(p) ~= n_prc + n_obs
                error('hgfx:perf01:config', 'Snapshot vector size mismatch.');
            end
            p_prc = p(1:n_prc)';
            p_obs = p(n_prc+1:end)';
            item.start_matches_matlab_priors = ...
                isequaln(p_prc, c_prc.priormus(:)') && ...
                isequaln(p_obs, c_obs.priormus(:)');
            if ~item.start_matches_matlab_priors
                item.status = 'MATLAB_PRIOR_START_MISMATCH';
            else
                r = struct();
                r.u = u;
                r.y = y;
                r.ign = find(isnan(u))';
                r.irr = union(find(isnan(u)), find(isnan(y)))';
                r.c_prc = c_prc;
                r.c_obs = c_obs;
                [~, infStates] = hgf_binary_unified(r, p_prc, 'trans');
                if size(infStates,1) ~= n
                    error('hgfx:perf01:shape', 'Unexpected inference horizon.');
                end
                logps = unitsq_sgm(r, infStates, p_obs);
                regular = true(n,1);
                regular(r.irr) = false;
                logll = sum(logps(regular));
                prior_prc = log_prior(p_prc, c_prc.priormus, c_prc.priorsas);
                prior_obs = log_prior(p_obs, c_obs.priormus, c_obs.priorsas);
                neg_joint = -(logll + prior_prc + prior_obs);
                item.neg_log_joint = neg_joint;
                item.neg_log_likelihood = -logll;
                item.trial_log_likelihood_count = numel(logps);
                if isfinite(neg_joint)
                    item.status = 'MATLAB_ONLY_OBJECTIVE_COMPLETED_HGFX_PARITY_NOT_ASSESSED';
                else
                    item.status = 'MATLAB_NONFINITE_OBJECTIVE';
                end
            end
        catch ME
            item.status = 'MATLAB_ERROR';
            item.error_identifier = ME.identifier;
            item.error_message = ME.message;
        end
        report.cells(end+1) = item; %#ok<AGROW>
    end
end

report.robustness = struct('case_id', 'robustness_masked_512', ...
    'status', 'MATLAB_NOT_RUN');
try
    d = jsondecode(fileread(fullfile(inputs_dir,'inputs','binary_512_s64.json')));
    u = double(d.u(1,:))';
    y = double(d.y(1,:))';
    u([32,128]) = NaN; y([32,128,64,256]) = NaN;
    snap = jsondecode(fileread(fullfile(inputs_dir,'configs','hgf_binary_512.json')));
    p = decode_numeric_records(snap.transformed_start_full);
    c_prc = hgf_binary_config();
    c_obs = unitsq_sgm_config();
    q = numel(c_prc.priormus);
    r = struct('u',u,'y',y,'ign',find(isnan(u))', ...
        'irr',union(find(isnan(u)),find(isnan(y)))', ...
        'c_prc',c_prc,'c_obs',c_obs);
    [~,infStates] = hgf_binary_unified(r,p(1:q)','trans');
    logps = unitsq_sgm(r,infStates,p(q+1:end)');
    if numel(logps) ~= 512
        error('hgfx:perf01:maskShape','Incorrect masked trial likelihood shape.');
    end
    report.robustness.status = 'MATLAB_ONLY_MASKED_COMPLETED_HGFX_PARITY_NOT_ASSESSED';
catch ME
    report.robustness.status = 'MATLAB_ERROR';
    report.robustness.error_identifier = ME.identifier;
    report.robustness.error_message = ME.message;
end

[outdir,~,~] = fileparts(output_path);
if ~isempty(outdir) && ~isfolder(outdir)
    mkdir(outdir);
end
fid = fopen(output_path, 'w');
if fid < 0
    error('hgfx:perf01:output', 'Cannot write MATLAB preflight report.');
end
cleaner = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(report));
disp('PERF-01 MATLAB reference-only preflight recorded; not a scientific-parity PASS.');
end

function p = decode_numeric_records(records)
if iscell(records)
    n = numel(records);
else
    n = numel(records);
end
p = NaN(1,n);
for k = 1:n
    if iscell(records)
        value = records{k};
    else
        value = records(k);
    end
    if isfield(value, 'decimal') && ~isempty(value.decimal)
        p(k) = str2double(value.decimal);
    elseif isfield(value, 'special')
        p(k) = str2double(value.special);
    else
        error('hgfx:perf01:decode', 'Unsupported numeric encoding.');
    end
end
end

function v = log_prior(p, mus, sas)
% Frozen HGF fitModel convention excludes undefined and fixed priors.
sas(isnan(sas)) = 0;
ix = find(sas);
terms = -0.5 .* log(2*pi.*sas(ix)) - 0.5 .* ((p(ix)-mus(ix)).^2) ./ sas(ix);
v = sum(terms);
end
