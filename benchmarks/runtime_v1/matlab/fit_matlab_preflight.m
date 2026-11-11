function fit_matlab_preflight(root, toolbox_root, output_path)
% Diagnostic full MATLAB fitModel boundary for preregistered 128-trial case.
% The 512/1024 default starts are invalid in both packages; automatic
% MATLAB random start resampling means those fits are NOT directly comparable.

addpath(genpath(toolbox_root));
r = struct();
r.schema = 'perf01-matlab-full-fitting-diagnostic-v1';
r.status = 'EXPLORATORY_UNFROZEN_NOT_TIMING';
r.matlab_version = version;
r.matlab_release = version('-release');
r.fitModel_resolved_path = which('fitModel');
r.hgf_binary_resolved_path = which('hgf_binary');
r.oracle_sha = '2437f4dc241541072722a2695ddeca7b44d83dd3';
r.cases = struct('case_id',{},'n_trials',{},'status',{}, ...
    'error_identifier',{},'error_message',{},'n_rand_init',{}, ...
    'optim',{},'traj',{});

for n = [128,512,1024]
    c = struct();
    c.case_id = sprintf('primary_fit_compat_full_%d',n);
    c.n_trials = n;
    c.status = 'NOT_RUN';
    c.error_identifier = '';
    c.error_message = '';
    c.n_rand_init = [];
    c.optim = struct();
    c.traj = struct();
    if n ~= 128
        c.status = 'BLOCKED_UNSTABLE_DEFAULT_START_MATLAB_RESAMPLES_HGFX_REJECTS';
        r.cases(end+1) = c; %#ok<AGROW>
        continue
    end
    data = jsondecode(fileread(fullfile(root,'inputs', ...
        sprintf('binary_%d_s64.json',n))));
    u = double(data.u(1,:))';
    y = double(data.y(1,:))';
    try
        copt = quasinewton_optim_config();
        if copt.nRandInit ~= 0 || copt.maxIter ~= 100
            error('hgfx:perf01:optimizer', ...
                'Unexpected frozen MATLAB optimization policy');
        end
        snap = jsondecode(fileread(fullfile(root,'configs','hgf_binary_128.json')));
        start = decode_records(snap.transformed_start_full);
        result = fitModel(y,u,'hgf_binary_config','unitsq_sgm_config', ...
                          'quasinewton_optim_config');
        c.n_rand_init = double(result.c_opt.nRandInit);
        if ~isequaln(result.optim.init(:),start(:))
            c.status = 'MATLAB_UNEXPECTED_START_OR_RESAMPLING';
        else
            c.status = 'MATLAB_FULL_FIT_COMPLETED_PARITY_NOT_ASSESSED';
        end
        o = result.optim;
        fields = {'init','final','H','Sigma','Corr','trialLogLlsplit', ...
            'negLl','negLj','LME','decompLME','AIC','BIC', ...
            'yhat','res','resAC'};
        for i=1:numel(fields)
            field=fields{i};
            c.optim.(field)=o.(field);
        end
        c.traj = result.traj;
    catch ME
        c.status = 'MATLAB_FULL_FIT_ERROR';
        c.error_identifier = ME.identifier;
        c.error_message = ME.message;
    end
    r.cases(end+1) = c; %#ok<AGROW>
end

[d,~,~] = fileparts(output_path);
if ~isfolder(d)
    mkdir(d);
end
fid = fopen(output_path,'w');
if fid < 0
    error('hgfx:perf01:output','Cannot write fitting report.');
end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(r));
fprintf('MATLAB full fit diagnostic report saved, no timing.\n');
end

function p=decode_records(records)
p=NaN(1,numel(records));
for k=1:numel(records)
    if iscell(records)
        item=records{k};
    else
        item=records(k);
    end
    if isfield(item,'decimal')
        p(k)=str2double(item.decimal);
    else
        p(k)=str2double(item.special);
    end
end
end
