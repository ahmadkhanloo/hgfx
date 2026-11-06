function subject7_termination_verbose_matlab(root, toolbox_root, original, output_path)
% PERF-01D: original MATLAB 8.2.0 public fitModel with source-native verbose only.
% Diagnostic flag only; full public output MUST be exactly identical to its
% normal-verbosity paired run on same MATLAB session/host. NO timing/fit PASS.
addpath(genpath(toolbox_root));
expectedHGFX='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
expectedMATLAB='2437f4dc241541072722a2695ddeca7b44d83dd3';
s=jsondecode(fileread(fullfile(original,'summary-41863441006.json')));
if ~strcmp(s.hgfx_sha,expectedHGFX) || ~strcmp(s.matlab_sha,expectedMATLAB) ...
   || ~strcmp(s.github_run_id,'41863441006') ...
   || s.subject_count~=64 ...
   || s.classification_counts.FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH~=1 ...
   || s.classification_counts.FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES~=63
    error('hgfx:perf01:original','Original 63/64 scientific NON-PASS not preserved');
end
originalRaw=jsondecode(fileread(fullfile(original,'matlab_raw.json')));
originalCase=originalRaw.cases(8);
if originalCase.subject_index_zero_based~=7 || ...
   ~strcmp(originalCase.status,'MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION') ...
   || originalCase.n_rand_init~=0 || ~originalCase.start_matches_frozen_snapshot
    error('hgfx:perf01:subject','Frozen subject-7 MATLAB fit identity invalid');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64 128]) || ~isequal(size(data.y),[64 128])
    error('hgfx:perf01:shape','Original input dimensions changed');
end
u=double(data.u(8,:))';y=double(data.y(8,:))';
opts=quasinewton_optim_config();
if opts.verbose || opts.maxIter~=100 || opts.nRandInit~=0 ...
  || opts.tolArg~=1e-3 || opts.tolGrad~=1e-3 ...
  || opts.maxStep~=1 || opts.maxRegu~=16 || opts.maxRst~=10 || ~opts.optIter
    error('hgfx:perf01:config','Original optimizer options differ');
end
% First: original complete public default-verbosity fit, source unchanged.
defaultConsole=evalc(['baseline=fitModel(y,u,''hgf_binary_config'',' ...
                     '''unitsq_sgm_config'',''quasinewton_optim_config'');']);
% Second: unchanged same model/inputs/public fit, ONLY flag verbose=true.
verboseOptions=opts;
verboseOptions.verbose=true;
verboseConsole=evalc(['verboseFit=fitModel(y,u,''hgf_binary_config'',' ...
                     '''unitsq_sgm_config'',verboseOptions);']);
if ~verboseFit.c_opt.verbose || baseline.c_opt.verbose || ...
   ~isequaln(baseline.optim.init(:),double(originalCase.optim.init(:))) || ...
   ~isequaln(verboseFit.optim.init(:),double(originalCase.optim.init(:)))
    error('hgfx:perf01:init','Original start or diagnostic-only toggle differs');
end
% Exact same-session, same-host, same-source output comparison of ALL fields.
% This is stricter than the inherited between-engine scientific tolerances.
fields={'init','final','H','Sigma','Corr','trialLogLlsplit', ...
        'negLl','negLj','LME','decompLME','AIC','BIC', ...
        'yhat','res','resAC','iter'};
exactPerField=struct();
for k=1:numel(fields)
    field=fields{k};
    exactPerField.(field)=isequaln(baseline.optim.(field),verboseFit.optim.(field));
end
trajectoryFields=fieldnames(baseline.traj);
if ~isequal(sort(trajectoryFields),sort(fieldnames(verboseFit.traj))) ...
        || numel(trajectoryFields)~=11
    error('hgfx:perf01:field','Original 11 HGF trialwise fields not retained');
end
exactPerTrajectory=struct();
for k=1:numel(trajectoryFields)
    field=trajectoryFields{k};
    exactPerTrajectory.(field)=isequaln(baseline.traj.(field),verboseFit.traj.(field));
end
allExact=all(structfun(@(a)logical(a),exactPerField)) && ...
         all(structfun(@(a)logical(a),exactPerTrajectory));
markers={
 'tol_arg','Converged on step size';
 'tol_grad','Converged on gradient size';
 'max_resets','Warning: optimization terminated because the maximum number of resets was reached.';
 'max_iter_warning','Warning: optimization terminated because the maximum number of iterations was reached.'};
events={};
for k=1:size(markers,1)
    if contains(verboseConsole,markers{k,2})
        events{end+1}=markers{k,1}; %#ok<AGROW>
    end
end
if numel(events)==1
    termination=events{1};
else
    termination='NOT_UNIQUELY_OBSERVED';
end
out=struct();
out.schema='perf01d-subject7-source-native-termination-matlab-v1';
out.status='AUTHOR_SIDE_VERBOSE_TERMINATION_NOT_A_SCIENCE_PASS_NO_TIMING';
out.frozen_hgfx_sha=expectedHGFX;
out.frozen_matlab_sha=expectedMATLAB;
out.original_64_fit_run_id='41863441006';
out.original_raw_sha256=s.raw_evidence_sha256;
out.source_input_sha256=s.hgfx_input_sha256;
out.source_config_sha256=s.hgfx_config_sha256;
out.subject_index_zero_based=7;
out.trials=128;
out.model='hgf_binary';
out.observation_model='unitsq_sgm';
out.n_rand_init=0;
out.changed_option='verbose_only_false_to_true';
out.same_session_normal_verbose_exact_all_fields=allExact;
out.same_session_exact_optim_fields=exactPerField;
out.same_session_exact_trajectory_fields=exactPerTrajectory;
out.source_native_termination=termination;
out.source_native_event_matches=events;
out.finite_history_slots=sum(isfinite(verboseFit.optim.iter.val));
out.allocated_history_slots=numel(verboseFit.optim.iter.val);
out.baseline_original_fit_final=baseline.optim.final;
out.verbose_public_fit_final=verboseFit.optim.final;
out.original_archived_fit_final=originalCase.optim.final;
out.baseline_full=baseline.optim;
out.verbose_full=verboseFit.optim;
out.baseline_traj=baseline.traj;
out.verbose_traj=verboseFit.traj;
out.verbose_console=verboseConsole;
out.normal_console=defaultConsole;
out.matlab_version=version;
out.matlab_fitModel_path=which('fitModel');
out.matlab_quasinewton_path=which('quasinewton_optim');
out.m_files_unchanged=true;
out.no_timing=true;
out.limitations={
 'Diagnostic-only verbose flag changed; no model, priors, data, optimizer tolerance or restart policy altered';
 'Exact same-host source-native termination marker does not establish independently approved fitting equivalence';
 'Original 63/64 full public MATLAB-versus-HGFX fitting remains NON-PASS, no benchmark timing'};
[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Could not write source-native MATLAB termination report');end
cleaner=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
fprintf('PERF01-D MATLAB source-native termination: %s, exact normal-vs-verbose: %d\n',termination,allExact);
if ~allExact
    error('hgfx:perf01:verbosity','Verbose changed full fitting output; no source-native termination claim allowed');
end
if ~strcmp(termination,'tol_arg') && ~strcmp(termination,'tol_grad') ...
        && ~strcmp(termination,'max_iter_warning') && ~strcmp(termination,'max_resets')
    error('hgfx:perf01:termination','Frozen MATLAB verbose did not provide one unambiguous termination cause');
end
end
