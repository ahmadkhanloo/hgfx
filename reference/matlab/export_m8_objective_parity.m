function export_m8_objective_parity(output_path)
%EXPORT_M8_OBJECTIVE_PARITY Export fixed-vector objective decomposition.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

payload = struct;
payload.metadata.schema_version = 'm8-1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.numeric_mode = 'CPU float64';
payload.metadata.matlab_version = version;
payload.metadata.perceptual_model = 'hgf_binary';
payload.metadata.observation_model = 'unitsq_sgm';
payload.metadata.objective_source = which('fitModel');

c_prc = hgf_binary_config;
p_prc = c_prc.priormus;
p_prc(13) = -2.7;
p_prc(14) = -5.4;
p_obs = log(20);

u = [0 1 1 0 1 0 0 1 1 0 1 1 0 0 1 1 0 1 0 1 1 0 1 0]';
y = [0 1 1 0 1 0 0 1 0 0 1 1 0 1 1 0 0 1 0 1 1 0 1 0]';
payload.cases.regular = run_case(u, y, p_prc, p_obs);

u2 = u;
y2 = y;
u2(6) = NaN;
y2(11) = NaN;
payload.cases.irregular_ignored = run_case(u2, y2, p_prc, p_obs);

payload.synthetic_prior = prior_case( ...
    [1 2 3 5], ...
    [0 2 0 4], ...
    [1 0 NaN 4]);

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m8:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M8 MATLAB objective export: PASS\n');
end

function out = run_case(inputs, responses, p_prc, p_obs)
r = struct;
r.u = inputs;
r.y = responses;
r.ign = find(isnan(r.u(:,1)))';
response_irr = find(isnan(r.y(:,1)))';
r.irr = unique([r.ign, response_irr]);
r.c_prc = hgf_binary_config;
r.c_obs = unitsq_sgm_config;

[~, infStates] = hgf_binary_unified(r, p_prc, 'trans');
trialLogLls = unitsq_sgm(r, infStates, p_obs);

regular = true(size(trialLogLls));
regular(r.irr) = false;
regularLogLls = trialLogLls(regular);
logLl = sum(regularLogLls);
if isnan(logLl)
    negLogLl = realmax;
else
    negLogLl = -logLl;
end

prc = prior_case(p_prc, r.c_prc.priormus, r.c_prc.priorsas);
obs = prior_case(p_obs, r.c_obs.priormus, r.c_obs.priorsas);
negLogJoint = -(logLl + prc.total + obs.total);

out = struct;
out.inputs = inputs;
out.responses = responses;
out.ptrans_prc = p_prc;
out.ptrans_obs = p_obs;
out.ignored_matlab_indices = r.ign;
out.irregular_matlab_indices = r.irr;
out.trial_log_likelihoods = trialLogLls;
out.regular_trial_log_likelihoods = regularLogLls;
out.log_likelihood = logLl;
out.neg_log_likelihood = negLogLl;
out.perceptual_prior = prc;
out.observation_prior = obs;
out.neg_log_joint = negLogJoint;
end

function out = prior_case(parameters, means, variances)
idx_values = variances;
idx_values(isnan(idx_values)) = 0;
idx = find(idx_values);
terms = -1/2 .* log(8*atan(1) .* variances(idx)) ...
        -1/2 .* (parameters(idx) - means(idx)).^2 ./ variances(idx);
out = struct;
out.matlab_indices = idx;
out.terms = terms;
out.total = sum(terms);
end
