function subject7_nested_objective_matlab(root,toolbox_root,anchors_path,output_path)
% PERF-01D author-side diagnostic, NOT a scientific PASS or benchmark.
% The EXACT frozen private fitModel negLogJoint reaches optimizer via obj_fun.
% Intercept only the public optimizer config handle; delegate ORIGINAL optimizer.
% Inputs fixed ahead of results: 2 x 25 native MATLAB history vectors.
addpath(genpath(toolbox_root));
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
hgfx='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
a=jsondecode(fileread(anchors_path));
if ~strcmp(a.schema,'perf01d-original-matlab-native-optimizer-anchors-v1') || ...
        ~strcmp(a.status,'FROZEN_50_ANCHORS_BEFORE_PRIVATE_OBJECTIVE_EVALUATION') || ...
        ~strcmp(a.original_fit_source_run,'42268256755') || ...
        ~strcmp(a.original_fit_source_commit,'331bb639dd65f3a3e2620b34f736a9b5156b8725') || ...
        ~strcmp(a.original_matlab_raw_sha256,'2133b60ca7dcd51b85d93dfad109f715bd8fe35fa71c2bd84ff4a63cac672139') || ...
        ~strcmp(a.frozen_hgfx_sha,hgfx) || ~strcmp(a.frozen_matlab_sha,ref) || ...
        ~strcmp(a.source_original_fitting,'63/64 NONPASS') || ...
        a.source_subject_zero_based~=7 || numel(a.cases)~=50 || ...
        ~isequal(a.anchor_indices_zero_based,0:24) || ...
        a.counts.MATLAB_1~=25 || a.counts.MATLAB_2~=25 || ~a.no_timing
    error('hgfx:perf01:nestedanchor','Prespecified 50 original native MATLAB anchors modified');
end
labels={a.cases.anchor_origin};
indexes=[a.cases.record_index_zero_based];
if ~isequal(labels(1:25),repmat({'MATLAB_1'},1,25)) || ...
   ~isequal(labels(26:50),repmat({'MATLAB_2'},1,25)) || ...
   ~isequal(indexes,[0:24,0:24])
    error('hgfx:perf01:nestedanchororder','Predeclared all-50 source order changed');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:source','Original 64x128 input changed');
end
y=double(data.y(8,:))';
u=double(data.u(8,:))';
cfg=quasinewton_optim_config();
original=cfg.opt_algo;
if ~strcmp(func2str(original),'quasinewton_optim') || ...
        cfg.nRandInit~=0 || cfg.maxIter~=100 || cfg.maxStep~=1 || ...
        cfg.maxRegu~=16 || cfg.maxRst~=10 || cfg.tolGrad~=1e-3 || ...
        cfg.tolArg~=1e-3 || cfg.verbose
    error('hgfx:perf01:optimizer','Original MATLAB optimizer config differs');
end
p=which('fitModel'); q=which('quasinewton_optim');
prefix=[strrep(toolbox_root,'\','/'),'/'];
if ~startsWith(strrep(p,'\','/'),prefix) || ...
   ~startsWith(strrep(q,'\','/'),prefix)
    error('hgfx:perf01:source','Frozen MATLAB reference resolved outside original toolbox');
end
hook_count=0; delegated=false;
cases=cell(1,50);
cfg.opt_algo=@instrumented_original_optimizer;
% The only non-native change in this diagnostic is the callback function handle.
console=evalc('fit=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
if hook_count~=1 || ~delegated
    error('hgfx:perf01:hook','FitModel did not supply the original optimizer handle');
end
entry=struct();
entry.status='INSTRUMENTED_PUBLIC_FIT_OUTPUT_NOT_ORACLE';
entry.start_matches_native=isequal(fit.optim.init(13:15),[-3,-6,3.871201010907891]);
entry.no_random_initializations=fit.c_opt.nRandInit==0;
entry.optim=struct();
fields={'init','final','H','Sigma','Corr','trialLogLlsplit',...
        'negLl','negLj','LME','decompLME','AIC','BIC','yhat','res','resAC'};
for j=1:numel(fields)
    k=fields{j};
    entry.optim.(k)=fit.optim.(k);
end
entry.traj=fit.traj;
if numel(fieldnames(entry.traj))~=11
    error('hgfx:perf01:inventory','Original 11 trajectory fields changed');
end
report=struct();
report.schema='perf01d-matlab-nested-objective-v1';
report.status='INSTRUMENTED_MATLAB_FITMODEL_REAL_NESTED_OBJECTIVE_NOT_SCIENCE_PASS';
report.source_run_id='42268256755';
report.source_matlab_raw_sha256='2133b60ca7dcd51b85d93dfad109f715bd8fe35fa71c2bd84ff4a63cac672139';
report.frozen_matlab_sha=ref;
report.frozen_hgfx_sha=hgfx;
report.source_input_sha256=a.source_input_sha256;
report.source_config_sha256=a.source_config_sha256;
report.subject_index_zero_based=7;
report.n_trials=128;
report.matlab_version=version;
report.matlab_release=version('-release');
report.matlab_fitmodel_path=p;
report.matlab_original_optim_path=q;
report.github_run_id=getenv('GITHUB_RUN_ID');
report.github_sha=getenv('GITHUB_SHA');
report.hook_call_count=hook_count;
report.original_optimizer_delegated=delegated;
report.captured_console_characters=numel(console);
report.no_timing=true;
report.instrumented_fit=entry;
report.cases=[cases{:}];
[folder,~,~]=fileparts(output_path);
if ~isfolder(folder);mkdir(folder);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:io','Cannot write MATLAB diagnostic report');end
cl=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
fprintf('Captured exact nested original fitModel objective at 50 source anchors; no timing or scientific promotion\n');

    function optres=instrumented_original_optimizer(obj,init,config)
        hook_count=hook_count+1;
        if ~isequal(init(:),[-3;-6;3.871201010907891]) || ...
                config.nRandInit~=0
            error('hgfx:perf01:hookstart','Original optimizer start changed');
        end
        for n=1:50
            case_source=a.cases(n);
            v=double(case_source.free_parameters(:));
            if numel(v)~=3 || ~all(isfinite(v))
                error('hgfx:perf01:vector','Original fixed source vector nonfinite');
            end
            row=struct();
            row.anchor_origin=case_source.anchor_origin;
            row.record_index_zero_based=case_source.record_index_zero_based;
            row.free_parameters=v';
            row.original_public_iter_val=case_source.original_public_iter_val;
            row.status='NOT_EVALUATED';
            row.nested_objective=[];
            row.error_identifier='';
            row.error_message='';
            try
                value=double(obj(v)); % the REAL private function passed by frozen fitModel
                if ~isscalar(value) || ~isfinite(value)
                    error('hgfx:perf01:objective','Nonfinite/non-scalar native nested objective');
                end
                row.status='EVALUATED';
                row.nested_objective=value;
            catch ME
                row.status='ERROR';
                row.error_identifier=ME.identifier;
                row.error_message=ME.message;
            end
            cases{n}=row;
        end
        % Same ORIGINAL algorithm and same ORIGINAL input config: not a fitted
        % endpoint override. Instrumentation neutrality must be externally checked.
        optres=original(obj,init,config);
        delegated=true;
    end
end
