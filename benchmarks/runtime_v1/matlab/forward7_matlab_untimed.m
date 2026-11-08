function forward7_matlab_untimed(root, toolbox_root, output_path)
% PERF-01C: seven original forward-only cases, complete arrays, NO TIMING.
% Diagnostic source output, not an independently approved benchmark.
expected_hgf = '2437f4dc241541072722a2695ddeca7b44d83dd3';
addpath(genpath(toolbox_root));
registry = jsondecode(fileread(fullfile(root,'inputs_manifest.json')));
cfgmanifest = jsondecode(fileread(fullfile(root,'resolved_configs_manifest.json')));
if ~strcmp(registry.matlab_oracle_sha, expected_hgf) || ...
        ~strcmp(cfgmanifest.matlab_reference_expected_sha, expected_hgf) || ...
        numel(registry.cases) ~= 28
    error('hgfx:perf01c:source','Original MATLAB source or case contract differs');
end
ids = {'primary_forward_128',...
       'secondary_ehgf_binary_forward_128',...
       'secondary_ehgf_binary_forward_512',...
       'secondary_ehgf_binary_forward_1024',...
       'secondary_uhgf_binary_forward_128',...
       'secondary_uhgf_binary_forward_512',...
       'secondary_uhgf_binary_forward_1024'};
models = {'hgf_binary','ehgf_binary','ehgf_binary','ehgf_binary',...
          'uhgf_binary','uhgf_binary','uhgf_binary'};
trials = [128,128,512,1024,128,512,1024];
fields = {'mu','sa','muhat','sahat','v','w','da','ud','psi','epsi','wt'};
rows = cell(1,numel(ids));
for k = 1:numel(ids)
    id = ids{k}; model = models{k}; n = trials(k);
    hit = find(strcmp({registry.cases.id},id));
    if numel(hit) ~= 1
        error('hgfx:perf01c:registry','Missing/duplicated forward ID: %s',id);
    end
    spec = registry.cases(hit);
    if ~strcmp(spec.model,model) || spec.n_trials ~= n || ...
            ~strcmp(spec.stage,'forward')
        error('hgfx:perf01c:registry','Original forward selection changed');
    end
    data = jsondecode(fileread(fullfile(root,spec.source_file)));
    snap = jsondecode(fileread(fullfile(root,'configs',...
        sprintf('%s_%d.json',model,n))));
    u = double(data.u(1,:))';
    y = double(data.y(1,:))';
    if numel(u) ~= n || any(~isfinite(u))
        error('hgfx:perf01c:input','Invalid unmasked original forward input');
    end
    theta = decode_records(snap.transformed_start_full);
    c_prc = feval([model '_config']);
    nprc = numel(c_prc.priormus);
    if numel(theta) < nprc || ~isequaln(theta(1:nprc),c_prc.priormus(:)')
        error('hgfx:perf01c:start','Original transformed prior/start mismatch');
    end
    r = struct('u',u,'y',y,'ign',[],'irr',[]);
    source_path = which(model);
    if isempty(source_path)
        error('hgfx:perf01c:path','Cannot resolve MATLAB forward model');
    end
    % Only the genuine frozen perceptual source is executed here.
    % No unitsq likelihood, priors, objective, fit or timer.
    [traj,states] = feval(model,r,theta(1:nprc),'trans');
    if ~isequal(size(states),[n,3,4]) || ...
            ~isequal(sort(fieldnames(traj)),sort(fields(:)))
        error('hgfx:perf01c:shape','Incomplete original forward outputs');
    end
    for j = 1:numel(fields)
        if size(traj.(fields{j}),1) ~= n
            error('hgfx:perf01c:shape','Wrong trial axis for %s',fields{j});
        end
    end
    row = struct();
    row.case_id = id;
    row.model = model;
    row.trials = n;
    row.subject_index = 0;
    row.source_sha256 = spec.source_sha256;
    row.resolved_function_path = source_path;
    row.status = 'MATLAB_UNTIMED_FORWARD_COMPLETED_HGFX_UNVERIFIED';
    row.inf_states = states;
    row.traj = traj;
    rows{k} = row;
end
report = struct();
report.schema = 'perf01c-forward7-matlab-untimed-v1';
report.status = 'DIAGNOSTIC_ONLY_NOT_BENCHMARK_NOT_SCIENTIFIC_PASS';
report.matlab_sha = expected_hgf;
report.matlab_release = version('-release');
report.original_case_denominator = 28;
report.forward_case_count = numel(rows);
report.cells = [rows{:}];
[folder,~,~] = fileparts(output_path);
if ~isfolder(folder), mkdir(folder); end
fid = fopen(output_path,'w');
if fid < 0, error('hgfx:perf01c:output','Cannot write original source'); end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
fprintf('MATLAB 7 forward-only complete outputs exported (UNTIMED / NOT FROZEN)\n');
end

function p = decode_records(records)
p = NaN(1,numel(records));
for i = 1:numel(records)
    if iscell(records), v = records{i}; else, v = records(i); end
    if isfield(v,'decimal')
        p(i) = str2double(v.decimal);
    elseif isfield(v,'special')
        p(i) = str2double(v.special);
    else
        error('hgfx:perf01c:decode','Unknown original float encoding');
    end
end
end
