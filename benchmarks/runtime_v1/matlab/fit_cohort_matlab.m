function fit_cohort_matlab(root, toolbox_root, output_path)
% PERF-01D: same 64 frozen 128-trial subjects; full MATLAB fitModel.
% Pure diagnostic: no timers, no altered starts, no subject omissions.
addpath(genpath(toolbox_root));
expected='2437f4dc241541072722a2695ddeca7b44d83dd3';
inputs_manifest=jsondecode(fileread(fullfile(root,'inputs_manifest.json')));
if ~strcmp(inputs_manifest.matlab_oracle_sha,expected)
    error('hgfx:perf01:identity','Unexpected MATLAB oracle commit.');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
snap=jsondecode(fileread(fullfile(root,'configs','hgf_binary_128.json')));
start=decode_records(snap.transformed_start_full);
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:dimensions','Expected exactly 64x128 data.');
end
co=quasinewton_optim_config;
if co.nRandInit~=0 || co.maxIter~=100
    error('hgfx:perf01:optimizer','MATLAB optimizer config differs from frozen reference.');
end

fields={'init','final','H','Sigma','Corr','trialLogLlsplit', ...
        'negLl','negLj','LME','decompLME','AIC','BIC', ...
        'yhat','res','resAC'};
rows=cell(1,64);
for k=1:64
    row=struct();
    row.model='hgf_binary';
    row.n_trials=128;
    row.subject_index_zero_based=k-1;
    row.status='NOT_RUN';
    row.start_matches_frozen_snapshot=false;
    row.n_rand_init=[];
    row.optimizer_iteration_count=[];
    row.optim=struct();
    row.traj=struct();
    row.console_characters=[];
    row.error_identifier='';
    row.error_message='';
    try
        u=double(data.u(k,:))';
        y=double(data.y(k,:))';
        % Only capture console for NON-TIMED scientific comparison.
        console=evalc(['fit = fitModel(y,u,' ...
            '''hgf_binary_config'',''unitsq_sgm_config'',' ...
            '''quasinewton_optim_config'');']);
        row.console_characters=numel(console);
        row.n_rand_init=double(fit.c_opt.nRandInit);
        row.start_matches_frozen_snapshot=isequaln(fit.optim.init(:),start(:));
        if row.n_rand_init~=0 || ~row.start_matches_frozen_snapshot
            row.status='MATLAB_UNEXPECTED_RESTART_OR_START';
        else
            row.status='MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION';
        end
        for i=1:numel(fields)
            field=fields{i};
            row.optim.(field)=fit.optim.(field);
        end
        row.traj=fit.traj;
        if isstruct(fit.optim.iter) && isfield(fit.optim.iter,'val')
            row.optimizer_iteration_count=numel(fit.optim.iter.val);
        else
            row.optimizer_iteration_count=0;
        end
    catch ME
        row.status='MATLAB_FULL_FIT_ERROR';
        row.error_identifier=ME.identifier;
        row.error_message=ME.message;
    end
    rows{k}=row;
end

r=struct();
r.schema='perf01-matlab-full-cohort-fit-v1';
r.status='UNFROZEN_DIAGNOSTIC_ONLY_NO_TIMING';
r.oracle_expected_sha=expected;
r.matlab_release=version('-release');
r.matlab_version=version;
r.fitModel_path=which('fitModel');
r.hgf_binary_path=which('hgf_binary');
r.model='hgf_binary';
r.observation_model='unitsq_sgm';
r.trials=128;
r.subjects=64;
r.cases=[rows{:}];
[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Cannot open full-cohort MATLAB report.');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(r));
fprintf('PERF-01 diagnostic all-64 MATLAB full fits recorded, no timing.\n');
end

function p=decode_records(items)
p=NaN(1,numel(items));
for i=1:numel(items)
    if iscell(items);v=items{i};else;v=items(i);end
    if isfield(v,'decimal')
        p(i)=str2double(v.decimal);
    elseif isfield(v,'special')
        p(i)=str2double(v.special);
    else
        error('hgfx:perf01:decode','Unsupported frozen numeric encoding.');
    end
end
end
