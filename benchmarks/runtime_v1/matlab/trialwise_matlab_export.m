function trialwise_matlab_export(root, toolbox_root, output_path)
% PERF-01: full scientific trialwise reference exports, no timing or fitting.
expected = '2437f4dc241541072722a2695ddeca7b44d83dd3';
addpath(genpath(toolbox_root));
manifest = jsondecode(fileread(fullfile(root, 'inputs_manifest.json')));
config_manifest = jsondecode(fileread(fullfile(root, 'resolved_configs_manifest.json')));
if ~strcmp(manifest.matlab_oracle_sha, expected) || ...
        ~strcmp(config_manifest.matlab_reference_expected_sha, expected)
    error('hgfx:perf01:reference', 'Unexpected reference SHA.');
end
models = {'hgf_binary', 'ehgf_binary', 'uhgf_binary'};
horizons = [128, 512, 1024];
rows = {};
for ni = 1:numel(horizons)
    n = horizons(ni);
    data = jsondecode(fileread(fullfile(root,'inputs', ...
        sprintf('binary_%d_s64.json',n))));
    for mi = 1:numel(models)
        model = models{mi};
        rows{end+1} = make_cell(root,data,model,n,false); %#ok<AGROW>
    end
    if n == 512
        rows{end+1} = make_cell(root,data,'hgf_binary',n,true); %#ok<AGROW>
    end
end
report = struct();
report.schema = 'hgfx-perf01-trialwise-matlab-v1';
report.protocol = 'hgfx-matlab-runtime-1';
report.oracle_sha = expected;
report.matlab_version = version;
report.matlab_release = version('-release');
report.status = 'EXPLORATORY_UNFROZEN_NO_PERFORMANCE';
report.cells = [rows{:}];
[outdir,~,~] = fileparts(output_path);
if ~isfolder(outdir)
    mkdir(outdir);
end
fid = fopen(output_path,'w');
if fid < 0
    error('hgfx:perf01:output', 'Cannot write trialwise reference evidence.');
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
fprintf('PERF-01 MATLAB reference-only trialwise evidence saved (%d cells)\n',numel(rows));
end

function row = make_cell(root,data,model,n,masked)
u = double(data.u(1,:))';
y = double(data.y(1,:))';
if masked
    u([32,128]) = NaN;
    y([32,128,64,256]) = NaN;
end
snap = jsondecode(fileread(fullfile(root,'configs',sprintf('%s_%d.json',model,n))));
theta = decode_records(snap.transformed_start_full);
r = struct();
r.u = u; r.y = y;
r.ign = find(isnan(u))';
r.irr = union(find(isnan(u)),find(isnan(y)))';
r.c_prc = feval([model '_config']);
r.c_obs = unitsq_sgm_config();
nprc = numel(r.c_prc.priormus);
nobs = numel(r.c_obs.priormus);
row = struct();
row.id = sprintf('%s_%d',model,n);
if masked
    row.id = 'robustness_masked_512';
end
row.model = model;
row.trials = n;
row.masked = masked;
row.resolved_function_path = which(model);
row.source_file = sprintf('binary_%d_s64.json',n);
row.start_matches_resolved_prior = nprc+nobs == numel(theta) && ...
    isequaln(theta(1:nprc),r.c_prc.priormus(:)') && ...
    isequaln(theta(nprc+1:end),r.c_obs.priormus(:)');
row.ignored_trial_ids_one_based = r.ign;
row.irregular_trial_ids_one_based = r.irr;
row.status = 'NOT_RUN';
row.error_identifier = '';
row.error_message = '';
row.prefix_diagnostic = struct();
row.inf_states = [];
row.traj = struct();
row.trial_log_likelihoods = [];
row.yhat = [];
row.residuals = [];
if ~row.start_matches_resolved_prior
    row.status = 'MATLAB_START_MISMATCH';
    return;
end
p_prc = theta(1:nprc);
p_obs = theta(nprc+1:end);
try
    [traj, states] = feval(model,r,p_prc,'trans');
    [logp,yhat,res] = unitsq_sgm(r,states,p_obs);
    if size(states,1) ~= n || numel(logp) ~= n
        error('hgfx:perf01:shape', 'Unexpected trialwise output size.');
    end
    row.status = 'MATLAB_COMPLETED_HGFX_UNVERIFIED';
    row.inf_states = states;
    row.traj = traj;
    row.trial_log_likelihoods = logp(:);
    row.yhat = yhat(:);
    row.residuals = res(:);
catch ME
    row.status = 'MATLAB_ERROR';
    row.error_identifier = ME.identifier;
    row.error_message = ME.message;
    if strcmp(model,'hgf_binary')
        row.prefix_diagnostic = sequential_prefix_probe(model,r,p_prc,n);
    end
end
end

function info = sequential_prefix_probe(model,r,theta,n)
% No binary search: hgf_check_trajectories uses prefix RMS, so validation
% is not necessarily monotone in prefix length.
info = struct();
info.policy = 'ALL_PREFIXES_IN_ASCENDING_ORDER_FROM_2';
info.first_invalid_prefix_length = [];
info.last_valid_prefix_length = [];
info.error_identifier = '';
for trials = 2:n
    sub = r;
    sub.u = r.u(1:trials,:);
    sub.y = r.y(1:trials,:);
    sub.ign = find(isnan(sub.u(:,1)))';
    sub.irr = union(find(isnan(sub.u(:,1))), find(isnan(sub.y(:,1))))';
    try
        feval(model,sub,theta,'trans');
        info.last_valid_prefix_length = trials;
    catch ME
        info.first_invalid_prefix_length = trials;
        info.error_identifier = ME.identifier;
        return;
    end
end
end

function p = decode_records(records)
p = NaN(1,numel(records));
for i = 1:numel(records)
    if iscell(records)
        v = records{i};
    else
        v = records(i);
    end
    if isfield(v,'decimal')
        p(i) = str2double(v.decimal);
    elseif isfield(v,'special')
        p(i) = str2double(v.special);
    else
        error('hgfx:perf01:decode','Unknown float encoding.');
    end
end
end
