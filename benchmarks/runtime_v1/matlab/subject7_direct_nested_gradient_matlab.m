function subject7_direct_nested_gradient_matlab(root,toolbox_root,anchors_path,output_path)
% PERF-01D: 50 prospectively frozen BFGS original-history vectors.
% Evaluate the REAL frozen fitModel private objective and its ORIGINAL
% Ridders gradient via public opt_algo callback. Delegate original optimizer.
% No source patches, timing, thresholds or scientific-gate changes.
addpath(genpath(toolbox_root));
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
h='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
a=jsondecode(fileread(anchors_path));
if ~strcmp(a.schema,'perf01d-original-bfgs-50-gradient-anchors-v1') || ...
   ~strcmp(a.status,'PRESPECIFIED_50_ORIGINAL_BFGS_ANCHORS') || ...
   ~strcmp(a.original_bfgs_source_run,'42187240378') || ...
   ~strcmp(a.original_hgfx_raw_sha256,'060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce') || ...
   ~strcmp(a.original_matlab_raw_sha256,'4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a') || ...
   ~strcmp(a.frozen_hgfx_sha,h) || ~strcmp(a.frozen_matlab_sha,ref) || ...
   ~strcmp(a.original_science,'63/64 NONPASS') || ...
   a.subject_index_zero_based~=7 || numel(a.cases)~=50 || ~a.no_timing
    error('hgfx:perf01:source','Original 50-case BFGS gradient prespec changed');
end
names={a.cases.anchor_origin};
indices=[a.cases.record_index_zero_based];
if ~isequal(names(1:25),repmat({'hgfx'},1,25)) || ...
   ~isequal(names(26:50),repmat({'matlab'},1,25)) || ...
   ~isequal(indices,[0:24,0:24])
    error('hgfx:perf01:inventory','Original 50-case source order changed');
end
if ~isequal(a.free_indices_zero_based,[12,13,14]) || ...
   ~isequal(a.start_free,[-3,-6,3.871201010907891])
    error('hgfx:perf01:start','Frozen scientific start changed');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original 64x128 input changed');
end
u=double(data.u(8,:))';y=double(data.y(8,:))';
cfg=quasinewton_optim_config();
original=cfg.opt_algo;
if ~strcmp(func2str(original),'quasinewton_optim') || ...
   cfg.nRandInit~=0 || cfg.maxIter~=100 || cfg.maxStep~=1 || ...
   cfg.maxRegu~=16 || cfg.maxRst~=10 || cfg.tolGrad~=1e-3 || ...
   cfg.tolArg~=1e-3 || cfg.verbose
    error('hgfx:perf01:optimizer','Original frozen config changed');
end
p=which('fitModel');q=which('quasinewton_optim');
prefix=[strrep(toolbox_root,'\','/'),'/'];
if ~startsWith(strrep(p,'\','/'),prefix) || ...
   ~startsWith(strrep(q,'\','/'),prefix)
    error('hgfx:perf01:resolution','Wrong MATLAB frozen source path');
end
% MATLAB nested function workspace requires outputs declared in advance.
native=[];instrumented=[];hook_count=0;delegated=false;
cases=cell(1,50);
native_console=evalc('native=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
original_cfg=cfg;
cfg.opt_algo=@capture_and_delegate;
instrumented_console=evalc('instrumented=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
if hook_count~=1 || ~delegated
    error('hgfx:perf01:hook','Expected one original objective callback and original optimizer delegation');
end
nv=pack_fit(native);
it=pack_fit(instrumented);
fields={'init','final','H','Sigma','Corr','trialLogLlsplit',...
        'negLl','negLj','LME','decompLME','AIC','BIC','yhat','res','resAC'};
neutral=true;
for i=1:numel(fields)
    k=fields{i};
    neutral=neutral && isequaln(nv.optim.(k),it.optim.(k));
end
trajfields=fieldnames(nv.traj);
if numel(trajfields)~=11 || numel(fieldnames(it.traj))~=11
    error('hgfx:perf01:traj','Historical 11 trajectory fields missing');
end
for i=1:numel(trajfields)
    k=trajfields{i};
    neutral=neutral && isequaln(nv.traj.(k),it.traj.(k));
end
report=struct();
report.schema='perf01d-direct-private-nested-bfgs-gradient-matlab-v1';
report.status='AUTHOR_SIDE_EXACT_NESTED_RIDDERS_NO_SCIENTIFIC_PASS';
report.original_bfgs_source_run='42187240378';
report.original_hgfx_raw_sha256=a.original_hgfx_raw_sha256;
report.original_matlab_raw_sha256=a.original_matlab_raw_sha256;
report.frozen_matlab_sha=ref;report.frozen_hgfx_sha=h;
report.source_input_sha256=a.source_input_sha256;
report.source_config_sha256=a.source_config_sha256;
report.subject_index_zero_based=7;report.n_trials=128;
report.matlab_version=version;report.matlab_release=version('-release');
report.matlab_fitmodel_path=p;report.matlab_optimizer_path=q;
report.github_run_id=getenv('GITHUB_RUN_ID');report.github_sha=getenv('GITHUB_SHA');
report.runner_name=getenv('RUNNER_NAME');
report.hook_count=hook_count;report.original_optimizer_delegated=delegated;
report.native_console_characters=numel(native_console);
report.instrumented_console_characters=numel(instrumented_console);
report.same_session_28_fields_isequaln=neutral;
report.native_fit=nv;report.instrumented_fit=it;
report.cases=[cases{:}];
report.no_timing=true;report.original_science='63/64 NONPASS';
report.independent_review='NOT_RECEIVED';report.perf01c='NOT_FROZEN';
[folder,~,~]=fileparts(output_path);
if ~isfolder(folder);mkdir(folder);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:io','Cannot save complete gradient source');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
fprintf('Real private nested MATLAB Ridders 50/50 saved; reviewer gate NOT passed\n');

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
        if ~isequal(init(:),[-3;-6;3.871201010907891]) || config.nRandInit~=0
            error('hgfx:perf01:hookstart','Original frozen start changed');
        end
        opts=struct('min_steps',10);
        for n=1:50
            prior=a.cases(n);
            x=double(prior.free_parameters(:));
            if numel(x)~=3 || ~all(isfinite(x))
                error('hgfx:perf01:vector','Original frozen anchor is nonfinite');
            end
            row=struct();
            row.anchor_origin=prior.anchor_origin;
            row.record_index_zero_based=prior.record_index_zero_based;
            row.free_parameters=x';
            row.status='NOT_EVALUATED';
            row.objective=[];row.ridders_gradient=[];row.ridders_error=[];
            row.error_identifier='';row.error_message='';
            try
                value=double(obj(x));
                [grad,err]=riddersgradient(obj,x,opts);
                if ~isscalar(value) || ~isfinite(value) || ...
                   numel(grad)~=3 || ~all(isfinite(grad(:))) || ...
                   numel(err)~=3 || ~all(isfinite(err(:)))
                    error('hgfx:perf01:nonfinite','Nonfinite actual nested gradient');
                end
                row.objective=value;
                row.ridders_gradient=double(grad(:))';
                row.ridders_error=double(err(:))';
                row.status='EVALUATED';
            catch ME
                row.status='ERROR';
                row.error_identifier=ME.identifier;
                row.error_message=ME.message;
            end
            cases{n}=row;
        end
        optres=original(obj,init,config);
        delegated=true;
    end
end
