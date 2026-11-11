function subject7_same_runner_matlab(root, toolbox_root, original, output_path)
% PERF-01D: prospectively locked TWO same-session MATLAB fitModel calls.
% No timers, no optimizer/start/data changes, no scientific verdict.
addpath(genpath(toolbox_root));
expected_h='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
expected_m='2437f4dc241541072722a2695ddeca7b44d83dd3';
summary=jsondecode(fileread(fullfile(original,'summary-41863441006.json')));
if ~strcmp(summary.hgfx_sha,expected_h) || ~strcmp(summary.matlab_sha,expected_m) ...
        || ~strcmp(summary.github_run_id,'41863441006') ...
        || summary.subject_count~=64 ...
        || summary.classification_counts.FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH~=1 ...
        || summary.classification_counts.FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES~=63
    error('hgfx:perf01:oldscience','Historical original 63/64 NONPASS modified');
end
src=fullfile(root,'inputs','binary_128_s64.json');
config=fullfile(root,'configs','hgf_binary_128.json');
data=jsondecode(fileread(src));
snap=jsondecode(fileread(config));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:inputs','Original 64x128 binary source changed');
end
start=decode_records(snap.transformed_start_full);
u=double(data.u(8,:))'; y=double(data.y(8,:))';
opts=quasinewton_optim_config();
if opts.maxIter~=100 || opts.nRandInit~=0 || opts.verbose || ...
        opts.tolGrad~=1e-3 || opts.tolArg~=1e-3 ...
        || opts.maxStep~=1 || opts.maxRegu~=16 || opts.maxRst~=10
    error('hgfx:perf01:optimizer','Frozen optimizer policy changed');
end
fitting=which('fitModel');
model=which('hgf_binary');
if ~startsWith(strrep(fitting,'\','/'),[strrep(toolbox_root,'\','/') '/']) || ...
        ~startsWith(strrep(model,'\','/'),[strrep(toolbox_root,'\','/') '/'])
    error('hgfx:perf01:resolution','MATLAB path is not original frozen toolbox');
end
fields={'init','final','H','Sigma','Corr','trialLogLlsplit', ...
        'negLl','negLj','LME','decompLME','AIC','BIC', ...
        'yhat','res','resAC'};
rows=cell(1,2);
for k=1:2
    row=struct();
    row.subject_index_zero_based=7; row.n_trials=128;
    row.model='hgf_binary'; row.observation='unitsq_sgm';
    % evalc ONLY for untimed scientific recording; disallowed as silent timer substitution.
    console=evalc(['fit=fitModel(y,u,''hgf_binary_config'',' ...
                   '''unitsq_sgm_config'',''quasinewton_optim_config'');']);
    if ~isequaln(fit.optim.init(:),start(:)) || double(fit.c_opt.nRandInit)~=0
        error('hgfx:perf01:start','Original start or restart semantics changed');
    end
    row.status='MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION';
    row.n_rand_init=double(fit.c_opt.nRandInit);
    row.start_matches_frozen_snapshot=true;
    row.console_characters=numel(console);
    row.optim=struct();
    for j=1:numel(fields)
        name=fields{j};
        row.optim.(name)=fit.optim.(name);
    end
    row.traj=fit.traj;
    if numel(fieldnames(row.traj))~=11
        error('hgfx:perf01:trajectory','11 original HGF trajectories required');
    end
    it=fit.optim.iter;
    if numel(it.val)~=101 || ~isequal(size(it.x),[101,3]) ...
            || sum(isfinite(it.val))~=25
        error('hgfx:perf01:history','Historical optimizer allocation/finite slots changed');
    end
    row.optimizer_history=struct('val',it.val,'x',it.x);
    row.optimizer_iteration_count=numel(it.val);
    row.finite_optimizer_history_slots=sum(isfinite(it.val));
    rows{k}=row;
end
report=struct();
report.schema='perf01d-subject7-same-runner-matlab-v1';
report.status='AUTHOR_SIDE_UNTIMED_FROZEN_MATLAB_TWO_PUBLIC_FITS_NO_PARITY_DECISION';
report.frozen_hgfx_sha=expected_h;
report.frozen_matlab_sha=expected_m;
report.original_64_fit_run='41863441006';
report.original_64_raw_sha256=summary.raw_evidence_sha256;
report.original_63_64_nonpass=true;
report.original_subject_index_zero_based=7;
report.source_input_sha256=summary.hgfx_input_sha256;
report.source_config_sha256=summary.hgfx_config_sha256;
report.matlab_release=version('-release');
report.matlab_version=version;
report.matlab_fitModel_resolved_path=fitting;
report.matlab_hgf_binary_resolved_path=model;
report.github_run_id=getenv('GITHUB_RUN_ID');
report.github_sha=getenv('GITHUB_SHA');
report.runner_name=getenv('RUNNER_NAME');
report.machine_arch=computer('arch');
report.matlab_max_computational_threads=maxNumCompThreads();
report.requested_shared_cpu_set=getenv('PERF01_CPU_SET');
report.fit_order={'MATLAB_1','MATLAB_2'};
report.cases=[rows{:}];
report.no_timing=true;
report.no_scientific_gate_promotion=true;
[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:export','Cannot open output file');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
fprintf('Original subject7 two MATLAB public fits saved on same runner, NO TIMING\n');
end

function p=decode_records(records)
p=NaN(1,numel(records));
for i=1:numel(records)
    if iscell(records);v=records{i};else;v=records(i);end
    if isfield(v,'decimal');p(i)=str2double(v.decimal);
    elseif isfield(v,'special');p(i)=str2double(v.special);
    else;error('hgfx:perf01:config','Frozen start encoding changed');
    end
end
end
