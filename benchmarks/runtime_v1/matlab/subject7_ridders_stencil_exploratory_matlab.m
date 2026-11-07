function subject7_ridders_stencil_exploratory_matlab(root,toolbox_root,manifest_path,output_path)
% PERF-01D post-result exploratory trace of REAL private fitModel objective.
% The single target is pre-recorded in protocol e1c3e2e. Do not call this
% a prospective validation cohort, a fit PASS or a benchmark/timed result.
addpath(genpath(toolbox_root));
m=jsondecode(fileread(manifest_path));
expected=[-1.1621811570388512,-6.37816839506084,-0.23738383160834042];
if ~strcmp(m.schema,'perf01d-posthoc-ridders-trace-manifest-v1') || ...
   ~strcmp(m.status,'POST_RESULT_SELECTION_NOT_A_SCIENTIFIC_GATE') || ...
   ~strcmp(m.protocol_commit_before_new_stencil_samples,'e1c3e2e83045896195701926a5f94fa361b0f091') || ...
   ~strcmp(m.original_50_probe_run_id,'42305573614') || ...
   ~strcmp(m.original_50_probe_executed_sha,'b9ff63685aac7ecd10a7cc4d1c33a4dc28699a62') || ...
   ~strcmp(m.original_frozen_hgfx_sha,'4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27') || ...
   ~strcmp(m.original_frozen_matlab_sha,'2437f4dc241541072722a2695ddeca7b44d83dd3') || ...
   ~strcmp(m.original_full_scientific_fits,'63/64 NONPASS') || ...
   ~strcmp(m.target_origin,'hgfx') || m.target_record_index_zero_based~=6 || ...
   ~isequal(double(m.target_free_parameters(:)'),expected) || ...
   m.ridders_min_steps~=10 || ~m.no_timing || ...
   ~strcmp(m.perf01c,'NOT_FROZEN') || ...
   ~strcmp(m.independent_scientific_review,'NOT_RECEIVED')
    error('hgfx:perf01:stencilmanifest','Post-result locked gradient outlier changed');
end
if ~strcmp(m.source_input_sha256,'6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae') || ...
   ~strcmp(m.source_config_sha256,'2523e0438fe28ca5f6e4bdf0c8b8530fb0b3cbe5cc50a87f5b5b55dbfd56c180')
    error('hgfx:perf01:stencilsources','Original input/config bytes changed');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:stencildata','Original 64 by 128 data changed');
end
u=double(data.u(8,:))'; y=double(data.y(8,:))';
cfg=quasinewton_optim_config();
original=cfg.opt_algo;
if ~strcmp(func2str(original),'quasinewton_optim') || ...
   cfg.nRandInit~=0 || cfg.maxIter~=100 || cfg.maxStep~=1 || ...
   cfg.maxRegu~=16 || cfg.maxRst~=10 || cfg.tolGrad~=1e-3 || ...
   cfg.tolArg~=1e-3 || cfg.verbose
    error('hgfx:perf01:stencilconfig','Frozen optimizer changed');
end
p=which('fitModel');q=which('quasinewton_optim');r=which('riddersgradient');
prefix=[strrep(toolbox_root,'\','/'),'/'];
if ~startsWith(strrep(p,'\','/'),prefix) || ...
   ~startsWith(strrep(q,'\','/'),prefix) || ...
   ~startsWith(strrep(r,'\','/'),prefix)
    error('hgfx:perf01:stencilpath','Original frozen MATLAB source resolution changed');
end
native=[];instrumented=[];hook_count=0;delegated=false;
trace_rows={}; trace_grad=[];trace_err=[];
native_console=evalc('native=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
cfg.opt_algo=@capture_and_delegate;
instrumented_console=evalc('instrumented=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
if hook_count~=1 || ~delegated || isempty(trace_grad) || isempty(trace_rows)
    error('hgfx:perf01:stencilhook','Original optimizer hook/gradient trace not executed');
end
nv=pack_fit(native);iv=pack_fit(instrumented);
fields={'init','final','H','Sigma','Corr','trialLogLlsplit',...
        'negLl','negLj','LME','decompLME','AIC','BIC','yhat','res','resAC'};
neutral=true;
for i=1:numel(fields)
    k=fields{i};
    neutral=neutral && isequaln(nv.optim.(k),iv.optim.(k));
end
trajfields=fieldnames(nv.traj);
if numel(trajfields)~=11 || numel(fieldnames(iv.traj))~=11
    error('hgfx:perf01:stenciltraj','Expected original 11 trajectory fields');
end
for i=1:numel(trajfields)
    k=trajfields{i};
    neutral=neutral && isequaln(nv.traj.(k),iv.traj.(k));
end
if numel(trace_grad)~=3 || numel(trace_err)~=3 || ...
   ~all(isfinite(trace_grad(:))) || ~all(isfinite(trace_err(:)))
    error('hgfx:perf01:stencilnan','Original MATLAB Ridders produced nonfinite gradient/error');
end
report=struct();
report.schema='perf01d-posthoc-ridders-matlab-trace-v1';
report.status='POST_RESULT_STENCIL_TRACE_NOT_A_SCIENTIFIC_PASS';
report.protocol_commit_before_new_stencil_samples='e1c3e2e83045896195701926a5f94fa361b0f091';
report.original_50_probe_run_id='42305573614';
report.original_frozen_hgfx_sha='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
report.original_frozen_matlab_sha='2437f4dc241541072722a2695ddeca7b44d83dd3';
report.source_50_anchor_sha256='d92690111b2fa128c045f29b39aa95110b5e5cd838f90c48a733400a3e537913';
report.source_50_matlab_sha256='90de6c75c13736fae95bc0645950ac0352546fd7262c4d5f70d97f8b9b14e978';
report.source_50_paired_sha256='2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d';
report.source_original_bfgs_hgfx_sha256='060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce';
report.source_original_bfgs_matlab_sha256='4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a';
report.source_input_sha256=m.source_input_sha256;
report.source_config_sha256=m.source_config_sha256;
report.subject_index_zero_based=7;report.n_trials=128;
report.target_free_parameters=expected;
report.matlab_version=version;report.matlab_release=version('-release');
report.matlab_fitmodel_path=p; report.matlab_optimizer_path=q;
report.matlab_ridders_path=r;
report.runner_name=getenv('RUNNER_NAME');report.github_run_id=getenv('GITHUB_RUN_ID');
report.github_sha=getenv('GITHUB_SHA');
report.hook_count=hook_count;report.original_optimizer_delegated=delegated;
report.same_session_28_fields_isequaln=neutral;
report.native_console_characters=numel(native_console);
report.instrumented_console_characters=numel(instrumented_console);
report.native_fit=nv;report.instrumented_fit=iv;
report.actual_private_objective_evaluation_calls=[trace_rows{:}];
report.actual_matlab_ridders_gradient=double(trace_grad(:))';
report.actual_matlab_ridders_error=double(trace_err(:))';
report.original_full_scientific_fits='63/64 NONPASS';
report.independent_scientific_review='NOT_RECEIVED';
report.perf01c='NOT_FROZEN';report.no_timing=true;
[folder,~,~]=fileparts(output_path);
if ~isfolder(folder);mkdir(folder);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:stencilio','Could not write complete private MATLAB trace');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
fprintf('Post-result real private MATLAB Ridders objective calls: %d, 28-field-neutral=%d; ORIGINAL FIT NONPASS\n',numel(trace_rows),neutral);

    function packed=pack_fit(fit)
        packed=struct();
        packed.status='NATIVE_OR_INSTRUMENTED_MATLAB_FIT_FOR_NEUTRALITY_ONLY';
        packed.optim=struct();
        flds={'init','final','H','Sigma','Corr','trialLogLlsplit',...
              'negLl','negLj','LME','decompLME','AIC','BIC','yhat','res','resAC'};
        for kk=1:numel(flds)
            key=flds{kk};
            packed.optim.(key)=fit.optim.(key);
        end
        packed.traj=fit.traj;
    end

    function optres=capture_and_delegate(obj,init,config)
        hook_count=hook_count+1;
        if ~isequal(init(:),[-3;-6;3.871201010907891]) || ...
           config.nRandInit~=0
            error('hgfx:perf01:stencilstart','Original free parameter init changed');
        end
        x=expected(:);
        [trace_grad,trace_err]=riddersgradient(@trace_obj,x,struct('min_steps',10));
        optres=original(obj,init,config);
        delegated=true;
        function v=trace_obj(z)
            v=double(obj(z));
            if ~isscalar(v) || ~isfinite(v)
                error('hgfx:perf01:stencilvalue','Nonfinite original private objective');
            end
            call=struct();
            call.free_parameters=double(z(:))';
            call.objective=v;
            trace_rows{end+1}=call;
        end
    end
end
