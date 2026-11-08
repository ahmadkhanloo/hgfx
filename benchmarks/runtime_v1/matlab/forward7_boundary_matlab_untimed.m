function forward7_boundary_matlab_untimed(root, toolbox_root, output_path)
% PERF-01C: proposed full forward-only call boundary, complete arrays, NO TIMER.
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
    % jsondecode produces a cell array for heterogeneous original case records
    % (the robustness case has extra mask fields); handle both representations.
    if iscell(registry.cases)
        all_ids = cellfun(@(item) item.id, registry.cases, ...
            'UniformOutput',false);
    else
        all_ids = {registry.cases.id};
    end
    hit = find(strcmp(all_ids,id));
    if numel(hit) ~= 1
        error('hgfx:perf01c:registry','Missing/duplicated forward ID: %s',id);
    end
    if iscell(registry.cases)
        spec = registry.cases{hit};
    else
        spec = registry.cases(hit);
    end
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
    r.c_prc = c_prc;
    r.c_obs = unitsq_sgm_config();
    source_path = which(model);
    if isempty(source_path) || ...
            ~startsWith(source_path,[toolbox_root filesep])
        error('hgfx:perf01c:path','Forward source outside pinned toolbox checkout');
    end
    % Candidate region: exactly this forward-only call. Its input preparation
    % is above, while validation/output serialization are below.
    % Neither wrapper includes clocks, likelihood, objective or fitting.
    [traj,states] = forward_only_call(model,r,theta(1:nprc));
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
    row.boundary_id = 'PERCEPTUAL_FORWARD_FULL_OUTPUT_CALL_V1';
    row.boundary_scope = 'FORWARD_ONLY_NO_OBSERVATION_NO_OBJECTIVE_NO_FIT';
    row.clock = 'ABSENT';
    row.inf_states = states;
    row.traj = traj;
    rows{k} = row;
end
report = struct();
report.schema = 'perf01c-forward7-matlab-boundary-untimed-v1';
report.candidate_boundary = 'PERCEPTUAL_FORWARD_FULL_OUTPUT_CALL_V1';
report.input_preparation = 'BEFORE_CALL_OUTSIDE_CANDIDATE_REGION';
report.output_shape_validation_and_serialization = ...
    'AFTER_CALL_OUTSIDE_CANDIDATE_REGION';
report.clock = 'ABSENT';
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
fprintf('MATLAB 7 proposed forward-call boundary outputs (UNTIMED / NOT FROZEN)\n');
end

function [traj,states] = forward_only_call(model,r,p)
% Single proposed computation region. No I/O, timers, response likelihood,
% optimizer, performance measurement or post-call serialization.
[traj,states] = feval(model,r,p,'trans');
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
