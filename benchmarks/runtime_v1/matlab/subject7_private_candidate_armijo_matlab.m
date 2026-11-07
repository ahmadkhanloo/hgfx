function subject7_private_candidate_armijo_matlab(root, toolbox_root, candidate_path, output_path)
% PERF-01D: two post-result-selected x6/T6 counterfactual step candidates.
% THREE actual frozen private fitModel objective calls; NO new fitting claims.
% The native original fit is an instrumentation-neutrality control only.
addpath(genpath(toolbox_root));
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
hgfx='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
d=jsondecode(fileread(candidate_path));
if ~strcmp(d.schema,'perf01d-postresult-source-one-step-original-record6-v1') || ...
   ~strcmp(d.source_original_frozen_hgfx,hgfx) || ...
   ~strcmp(d.source_original_frozen_matlab,ref) || ...
   ~strcmp(d.source_original_64_public_fit_science,'63/64 SCIENTIFIC NONPASS') || ...
   d.subject_index_zero_based~=7 || d.original_trial_count~=128 || ...
   d.original_history_record_zero_based~=6 || ...
   ~d.post_result_selection || ~d.one_step_is_NOT_a_completed_fitting_result || ...
   ~strcmp(d.independent_scientific_review,'NOT_RECEIVED') || ...
   ~strcmp(d.perf01c,'NOT_FROZEN') || ~strcmp(d.timing,'NOT_RUN')
    error('hgfx:perf01:candidate','Original post-result candidate source identity changed');
end
expected_x6=[-1.1621811570388512;-6.37816839506084;-0.23738383160834042];
x6=double(d.one_identical_x(:));
if ~isequal(x6,expected_x6) || ~isequal(double(d.source_original_zero_based_subject7_4_plus_4_mismatches.traj_mu),4)
    % MATLAB jsondecode maps JSON keys containing periods to 'traj_mu'.
    error('hgfx:perf01:incident','Frozen original x6 or failed public fit evidence changed');
end
dh=d.same_T6_and_x6_one_step_directions.hgfx_original_source_gradient;
dm=d.same_T6_and_x6_one_step_directions.real_matlab_private_gradient_at_exact_hgfx_source_x;
qh=double(dh.source_next_full_step_free_x(:));
qm=double(dm.source_next_full_step_free_x(:));
if numel(qh)~=3 || numel(qm)~=3 || ...
   ~all(isfinite(qh)) || ~all(isfinite(qm)) || ...
   isequal(qh,qm) || isequal(qh,x6) || isequal(qm,x6) || ...
   dh.source_current_value~=108.28848680066957 || ...
   dm.source_current_value~=108.28848680066957 || ...
   ~dh.original_source_clipping_applied || ~dm.original_source_clipping_applied
    error('hgfx:perf01:steps','Frozen original BFGS same-state candidates changed');
end
names={'original_hgfx_source_x6','hgfx_original_source_gradient',...
       'real_matlab_private_gradient_at_exact_hgfx_source_x'};
points={x6,qh,qm};
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original 64x128 synthetic scientific data changed');
end
u=double(data.u(8,:))';y=double(data.y(8,:))';
cfg=quasinewton_optim_config();
original=cfg.opt_algo;
if ~strcmp(func2str(original),'quasinewton_optim') || ...
   cfg.nRandInit~=0 || cfg.maxIter~=100 || cfg.maxStep~=1 || ...
   cfg.maxRegu~=16 || cfg.maxRst~=10 || cfg.tolGrad~=1e-3 || ...
   cfg.tolArg~=1e-3 || cfg.verbose
    error('hgfx:perf01:optimizer','Original frozen optimizer config changed');
end
prefix=[strrep(toolbox_root,'\','/'),'/'];
p=which('fitModel');q=which('quasinewton_optim');
if ~startsWith(strrep(p,'\','/'),prefix) || ...
   ~startsWith(strrep(q,'\','/'),prefix)
    error('hgfx:perf01:source','Wrong frozen MATLAB fitModel/optimizer source paths');
end
native=[];instrumented=[];hook_count=0;delegated=false;
rows=cell(1,3);
native_console=evalc('native=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
cfg.opt_algo=@capture_and_delegate;
instrumented_console=evalc('instrumented=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
optim_fields={'init','final','H','Sigma','Corr','trialLogLlsplit',...
              'negLl','negLj','LME','decompLME','AIC','BIC','yhat','res','resAC'};
traj_fields=fieldnames(native.traj);
neutral=true;
for k=1:numel(optim_fields)
    f=optim_fields{k};
    neutral=neutral && isfield(native.optim,f) && ...
        isfield(instrumented.optim,f) && ...
        isequaln(native.optim.(f),instrumented.optim.(f));
end
if numel(traj_fields)~=11 || numel(fieldnames(instrumented.traj))~=11
    neutral=false;
end
for k=1:numel(traj_fields)
    f=traj_fields{k};
    neutral=neutral && isfield(instrumented.traj,f) && ...
        isequaln(native.traj.(f),instrumented.traj.(f));
end
if isempty(rows{1}) || isempty(rows{2}) || isempty(rows{3})
    error('hgfx:perf01:callback','Not all three private objective call outcomes retained');
end
if strcmp(rows{1}.status,'EVALUATED_FINITE')
    v0=rows{1}.private_objective;
    for k=2:3
        if strcmp(rows{k}.status,'EVALUATED_FINITE')
            rows{k}.private_armijo_delta_lhs=rows{k}.private_objective-v0;
            rows{k}.private_armijo_full_step= ...
                (rows{k}.private_armijo_delta_lhs<rows{k}.original_armijo_delta_rhs);
        end
    end
end
report=struct();
report.schema='perf01d-actual-private-matlab-candidate-armijo-v1';
report.status='AUTHOR_SIDE_THREE_ACTUAL_PRIVATE_OBJECTIVE_CALLS_REVIEW_PENDING';
report.source_original_candidate_sha256='b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144';
report.frozen_hgfx_sha=hgfx;report.frozen_matlab_sha=ref;
report.original_science='63/64 SCIENTIFIC NONPASS';
report.original_subject_zero_based=7;report.original_trial_count=128;
report.original_hgfx_source_x6=x6';
report.original_x6_expected_hgfx_value=108.28848680066957;
report.native_reference_baseline_equal_original_x6= ...
    strcmp(rows{1}.status,'EVALUATED_FINITE') && ...
    rows{1}.private_objective==108.28848680066957;
report.matlab_version=version;report.matlab_release=version('-release');
report.matlab_fitmodel_path=p;report.matlab_optimizer_path=q;
report.github_run_id=getenv('GITHUB_RUN_ID');report.tested_sha=getenv('GITHUB_SHA');
report.runner_name=getenv('RUNNER_NAME');
report.hook_count=hook_count;report.original_optimizer_delegated=delegated;
report.native_console_characters=numel(native_console);
report.instrumented_console_characters=numel(instrumented_console);
report.compared_stable_field_count=numel(optim_fields)+numel(traj_fields);
report.native_instrumented_stable_fields_identical=neutral;
% Preserve heterogeneous base/candidate result fields as a JSON cell array.
% Struct-array concatenation requires identical field sets and previously
% failed AFTER the real objective calls, before the evidence was written.
report.calls=rows;
report.independent_scientific_review='NOT_RECEIVED';
report.perf01c='NOT_FROZEN';report.timing='NOT_RUN';
report.post_result_selected_counterfactual=true;
report.not_an_original_matlab_optimizer_branch_trace=true;
[folder,~,~]=fileparts(output_path);
if ~isfolder(folder);mkdir(folder);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:write','Cannot preserve raw private objective evidence');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
if hook_count~=1 || ~delegated || ~neutral || report.compared_stable_field_count~=26
    error('hgfx:perf01:neutrality','Original native optimizer callback was not strictly neutral');
end
fprintf('Three frozen private MATLAB objective calls archived; original 63/64 NONPASS remains\n');

    function optres=capture_and_delegate(obj,init,config)
        hook_count=hook_count+1;
        if ~isequal(init(:),[-3;-6;3.871201010907891]) || ...
           config.nRandInit~=0
            error('hgfx:perf01:hookstart','Frozen scientific start changed');
        end
        for n=1:3
            row=struct();
            row.name=names{n};row.free_x=points{n}';
            row.status='NOT_EVALUATED';row.private_objective=[];
            row.error_identifier='';row.error_message='';
            if n>1
                if n==2; saved=dh; else; saved=dm; end
                row.original_armijo_delta_rhs=double(saved.original_armijo_delta_RHS_using_unclipped_slope);
                row.previous_hgfx_objective_at_candidate=double(saved.new_evaluated_hgfx_objective_at_candidate);
            end
            try
                value=double(obj(points{n}));
                if ~isscalar(value) || ~isreal(value)
                    error('hgfx:perf01:value','Actual frozen MATLAB objective not a real scalar');
                end
                row.private_objective=value;
                if ~isfinite(value)
                    row.status='NONFINITE';
                elseif value==realmax
                    row.status='REALMAX_SENTINEL';
                else
                    row.status='EVALUATED_FINITE';
                end
            catch ME
                row.status='EXCEPTION';
                row.error_identifier=ME.identifier;
                row.error_message=ME.message;
            end
            rows{n}=row;
        end
        optres=original(obj,init,config);
        delegated=true;
    end
end
