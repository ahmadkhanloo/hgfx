function run_compstat_rev24_matlab(input_path, output_path)
% REV-2.4 MATLAB Panel-G ONLY: consumes frozen 600-vector manifest as-is.
% No optimizer, fitting, random-number generation, filters or new cases.
% UNVALIDATED SOURCE pending true MATLAB HGF 8.2.0 execution and review.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
toolbox = fullfile(root, 'external', 'hgf-toolbox');
expected_ref = '2437f4dc241541072722a2695ddeca7b44d83dd3';
expected_release = '4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
[status, git_head] = system(sprintf('git -C "%s" rev-parse HEAD', toolbox));
assert(status == 0 && strcmp(strtrim(git_head), expected_ref), ...
    'REV24:referenceCommitMismatch', 'Frozen MATLAB HGF source is not pinned.');
addpath(genpath(toolbox));

data = jsondecode(fileread(input_path));
assert(strcmp(data.protocol, 'compstat-rev2-4-objective-cross-eval-v1'));
assert(strcmp(data.matlab_reference_commit, expected_ref));
assert(strcmp(data.release_source_commit_declared, expected_release));
assert(data.n_per_model == 200 && data.trials == 128);
t = (0:127)';
u = double(mod(37*t+11, 101) < 51);
y = double(mod(29*t+3, 97) < 47);
assert(isequal(u, double(data.inputs(:))) && ...
       isequal(y, double(data.responses(:))), ...
       'REV24:inputMismatch', 'Frozen synthetic trial data changed.');

names = {'hgf_binary', 'ehgf_binary', 'uhgf_binary'};
groups = data.strata;
assert(numel(groups) == 3);
out.protocol = data.protocol;
out.source = 'matlab';
out.release_source_commit = expected_release;
out.matlab_reference_commit = expected_ref;
out.manifest_sha256 = data.manifest_sha256;
out.inputs_binary64_le_sha256 = data.inputs_binary64_le_sha256;
out.responses_binary64_le_sha256 = data.responses_binary64_le_sha256;
out.matlab_version = version;
out.objective_method = 'frozen HGF config and perceptual/observation functions';
out.scientific_parity_status = 'NOT_ASSESSED_NO_HGFX_PAIR';
out.cases = cell(1, 600);
index = 0;
for g = 1:numel(groups)
    group = get_element(groups, g);
    model = names{g};
    assert(strcmp(char(group.model), model));
    assert(strcmp(char(group.observation_model), 'unitsq_sgm'));
    rows = group.rows;
    assert(numel(rows) == 200);
    pc = feval([model '_config']);
    oc = unitsq_sgm_config();
    means = [pc.priormus(:)', oc.priormus(:)'];
    variances = [pc.priorsas(:)', oc.priorsas(:)'];
    target_means = parse_ieee(group.prior_means_full);
    target_variances = parse_ieee(group.prior_variances_full_ieee);
    assert(isequaln(means, target_means) && ...
           isequaln(variances, target_variances), ...
           'REV24:configMismatch', 'MATLAB vs HGFX default priors differ.');
    free = find(~isnan(variances) & variances ~= 0)-1;
    assert(isequal(free(:)', double(group.free_indices_zero_based(:)')), ...
           'REV24:freeIndexMismatch', 'Different free parameter ordering.');
    for k = 1:numel(rows)
        row = get_element(rows, k);
        assert(strcmp(char(row.case_id), ...
            sprintf('REV24-G-%s-%03d', model, k-1)));
        index = index + 1;
        out.cases{index} = evaluate_case(model, row, group, ...
                                         u, y, pc, oc);
    end
end
assert(index == 600);
directory = fileparts(output_path);
if ~isempty(directory) && ~exist(directory, 'dir')
    mkdir(directory);
end
assert(~exist(output_path, 'file'), ...
    'REV24:overwrite', 'Refuse to overwrite original raw objective results.');
fid = fopen(output_path, 'w');
assert(fid >= 0, 'REV24:writeError', 'Could not open output JSON.');
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(out, 'PrettyPrint', true));
fprintf('REV-2.4 MATLAB source-only: 600 cases retained; NO parity PASS\n');
end

function r = evaluate_case(model, row, group, u, y, pc, oc)
r.case_id = char(row.case_id);
r.case_sha256 = char(row.case_sha256);
r.model = model;
r.config_sha256 = char(group.config_sha256);
r.valid = false;
r.rval = -1;
r.neg_log_likelihood = 'NaN';
r.neg_log_joint = 'NaN';
r.log_likelihood = 'NaN';
r.trial_log_likelihoods = {};
r.perceptual_prior_total = 'NaN';
r.observation_prior_total = 'NaN';
r.error_type = '';
r.error_message = '';
try
    full = parse_ieee(row.full_transformed);
    prc_length = numel(pc.priormus);
    expected_length = prc_length + numel(oc.priormus);
    assert(numel(full) == expected_length);
    free = double(group.free_indices_zero_based(:)') + 1;
    assert(isequal(full(free), double(row.free_transformed(:)')));
    r_data.u = u;
    r_data.y = y;
    r_data.ign = find(isnan(u))';
    r_data.irr = unique([r_data.ign, find(isnan(y))']);
    r_data.c_prc = pc;
    r_data.c_obs = oc;
    % Dispatch through the frozen configuration's original perceptual wrapper.
    % Only hgf_binary_unified exists; eHGF/uHGF have distinct wrappers.
    perceptual = pc.prc_fun;
    [~, states] = perceptual(r_data, full(1:prc_length), 'trans');
    ll = unitsq_sgm(r_data, states, full(prc_length+1:end));
    ll = double(ll(:)');
    regular = ll;
    regular(r_data.irr) = [];
    logLl = sum(regular);
    if isnan(logLl)
        negLl = realmax;
    else
        negLl = -logLl;
    end
    prc_idx = find(~isnan(pc.priorsas) & pc.priorsas ~= 0);
    obs_idx = find(~isnan(oc.priorsas) & oc.priorsas ~= 0);
    p_prc = full(1:prc_length);
    p_obs = full(prc_length+1:end);
    prc_terms = -0.5 .* log(8*atan(1).*pc.priorsas(prc_idx)) ...
        -0.5 .* (p_prc(prc_idx)-pc.priormus(prc_idx)).^2 ...
        ./ pc.priorsas(prc_idx);
    obs_terms = -0.5 .* log(8*atan(1).*oc.priorsas(obs_idx)) ...
        -0.5 .* (p_obs(obs_idx)-oc.priormus(obs_idx)).^2 ...
        ./ oc.priorsas(obs_idx);
    p_prc_total = sum(prc_terms);
    p_obs_total = sum(obs_terms);
    negLj = -(logLl + p_prc_total + p_obs_total);
    r.rval = 0;
    r.log_likelihood = ieee_one(logLl);
    r.neg_log_likelihood = ieee_one(negLl);
    r.neg_log_joint = ieee_one(negLj);
    r.trial_log_likelihoods = arrayfun(@ieee_one, ll, ...
                                      'UniformOutput', false);
    r.perceptual_prior_total = ieee_one(p_prc_total);
    r.observation_prior_total = ieee_one(p_obs_total);
    r.valid = numel(ll) == 128 && all(isfinite(ll(:))) && ...
        isfinite(logLl) && isfinite(negLl) && isfinite(negLj);
catch ME
    r.error_type = ME.identifier;
    r.error_message = ME.message;
end
end

function numeric = parse_ieee(value)
if isnumeric(value)
    numeric = double(value(:)');
    return;
end
if iscell(value)
    numeric = zeros(1, numel(value));
    for i = 1:numel(value)
        numeric(i) = parse_scalar(value{i});
    end
    return;
end
if isstring(value)
    numeric = cellfun(@parse_scalar, cellstr(value));
    return;
end
error('REV24:encoding', 'Unsupported IEEE scalar/array JSON encoding.');
end

function number = parse_scalar(value)
if isnumeric(value) && isscalar(value)
    number = double(value);
elseif ischar(value) || isstring(value)
    v = char(value);
    if strcmp(v, 'NaN')
        number = NaN;
    elseif strcmp(v, '+Inf')
        number = Inf;
    elseif strcmp(v, '-Inf')
        number = -Inf;
    else
        error('REV24:encoding', 'Unexpected string in IEEE vector.');
    end
else
    error('REV24:encoding', 'Unexpected scalar type in IEEE vector.');
end
end

function value = ieee_one(x)
if isnan(x)
    value = 'NaN';
elseif isinf(x) && x > 0
    value = '+Inf';
elseif isinf(x)
    value = '-Inf';
else
    value = double(x);
end
end

function value = get_element(elements, index)
if iscell(elements)
    value = elements{index};
else
    value = elements(index);
end
end
