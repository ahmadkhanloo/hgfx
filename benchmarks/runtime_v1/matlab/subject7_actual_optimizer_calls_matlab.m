function subject7_actual_optimizer_calls_matlab(root, toolbox_root, output_path, raw_mat_path)
% Author-side, UNTImED: actual ORIGINAL MATLAB-owned optimizer objective calls.
% Frozen MATLAB quasinewton_optim source is NEVER changed; wrapper logs calls.
% This is NOT MATLAB-vs-HGFX parity, independent review, or a benchmark.
addpath(genpath(toolbox_root));
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
hgfx='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
prefix=[strrep(toolbox_root,'\','/'),'/'];
p=which('fitModel');q=which('quasinewton_optim');
if ~startsWith(strrep(p,'\','/'),prefix) || ...
   ~startsWith(strrep(q,'\','/'),prefix)
    error('hgfx:perf01:source','Frozen MATLAB source path wrong');
end
source_lines=regexp(fileread(q),'\r\n|\n|\r','split');
normalized=cellfun(@(s) regexprep(s,'\s+',''),source_lines,'UniformOutput',false);
input_line=find(strcmp(normalized,'val=f(x);'));
candidate_line=find(strcmp(normalized,'newval=f(newx);'));
if numel(input_line)~=2 || numel(candidate_line)~=1 || ...
   input_line(1)>=candidate_line || candidate_line>=input_line(2)
    error('hgfx:perf01:source','Frozen actual optimizer objective callsite lines changed');
end

data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Frozen 64 by 128 data missing');
end
u=double(data.u(8,:))'; y=double(data.y(8,:))';
cfg=quasinewton_optim_config();
original=cfg.opt_algo;
if ~strcmp(func2str(original),'quasinewton_optim') || ...
   cfg.nRandInit~=0 || cfg.maxIter~=100 || cfg.maxStep~=1 || ...
   cfg.maxRegu~=16 || cfg.maxRst~=10 || cfg.tolGrad~=1e-3 || ...
   cfg.tolArg~=1e-3 || ~cfg.optIter || cfg.verbose
    error('hgfx:perf01:config','Original frozen optimizer settings changed');
end
native=[]; instrumented=[]; captured_optim=[];
hook_count=0; delegated=false; obj_callback=[];
total_calls=0; indirect_calls=0;
direct=cell(1,0); counts=[0,0,0,0];
native_console=evalc('native=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
cfg.opt_algo=@capture_and_delegate;
instrumented_console=evalc('instrumented=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');

opt_fields={'init','final','H','Sigma','Corr','trialLogLlsplit',...
            'negLl','negLj','LME','decompLME','AIC','BIC','yhat','res','resAC'};
traj_fields=fieldnames(native.traj);
neutral=true;
if numel(traj_fields)~=11 || numel(fieldnames(instrumented.traj))~=11
    neutral=false;
end
for kk=1:numel(opt_fields)
    f=opt_fields{kk};
    neutral=neutral && isfield(native.optim,f) && ...
        isfield(instrumented.optim,f) && ...
        isequaln(native.optim.(f),instrumented.optim.(f));
end
for kk=1:numel(traj_fields)
    f=traj_fields{kk};
    neutral=neutral && isfield(instrumented.traj,f) && ...
        isequaln(native.traj.(f),instrumented.traj.(f));
end
history_equal=isfield(native.optim,'iter') && ...
    isfield(instrumented.optim,'iter') && ...
    isequaln(native.optim.iter,instrumented.optim.iter);
if ~history_equal || isempty(native.optim.iter) || ...
   ~isfield(native.optim.iter,'val') || ~isfield(native.optim.iter,'x')
    error('hgfx:perf01:history','Actual frozen original optimizer history not available');
end
v=native.optim.iter.val;
k=find(isfinite(v));
if numel(k)~=25 || ~isequal(size(native.optim.iter.x),[101,3]) || ...
   ~all(isfinite(native.optim.iter.x(k,:)),'all')
    error('hgfx:perf01:history','Original history inventory changed');
end
if numel(direct)~=sum(counts) || ...
   total_calls~=(numel(direct)+indirect_calls)
    error('hgfx:perf01:calls','Actual source call accounting mismatch');
end
native_public=struct('optim',struct(),'traj',struct());
instrumented_public=struct('optim',struct(),'traj',struct());
for kk=1:numel(opt_fields)
    f=opt_fields{kk};
    native_public.optim.(f)=native.optim.(f);
    instrumented_public.optim.(f)=instrumented.optim.(f);
end
for kk=1:numel(traj_fields)
    f=traj_fields{kk};
    native_public.traj.(f)=native.traj.(f);
    instrumented_public.traj.(f)=instrumented.traj.(f);
end
native_iter=native.optim.iter;
instrumented_iter=instrumented.optim.iter;
metadata=struct();
metadata.schema='perf01d-native-matlab-direct-objective-calls-v1';
metadata.status='AUTHOR_SIDE_DIRECT_SOURCE_CALLS_REVIEW_PENDING';
metadata.frozen_matlab_sha=ref; metadata.frozen_hgfx_sha=hgfx;
metadata.matlab_fitmodel_path=p; metadata.matlab_optimizer_path=q;
metadata.source_initial_line=double(input_line(1));
metadata.source_linesearch_line=double(candidate_line);
metadata.source_reset_line=double(input_line(2));
metadata.subject_index_zero_based=7; metadata.original_trial_count=128;
metadata.original_science='63/64 SCIENTIFIC NONPASS';
metadata.original_failure_mu=4; metadata.original_failure_muhat=4;
metadata.opt_fields=opt_fields; metadata.traj_fields=traj_fields;
metadata.compared_26_fields=26;
metadata.native_instrumented_stable_identical=neutral;
metadata.native_instrumented_history_identical=history_equal;
metadata.hook_count=hook_count; metadata.delegated=delegated;
metadata.total_calls=total_calls;metadata.indirect_calls=indirect_calls;
metadata.direct_counts=counts; metadata.direct_call_count=numel(direct);
metadata.finite_native_history_count=numel(k);
metadata.matlab_version=version;metadata.matlab_release=version('-release');
metadata.github_run_id=getenv('GITHUB_RUN_ID');
metadata.tested_sha=getenv('GITHUB_SHA');
metadata.runner_name=getenv('RUNNER_NAME');
metadata.native_console_characters=numel(native_console);
metadata.instrumented_console_characters=numel(instrumented_console);
metadata.independent_review='NOT_RECEIVED';
metadata.perf01c='NOT_FROZEN';metadata.timing='NOT_RUN';
metadata.not_an_original_optimizer_source_patch=true;
metadata.not_a_source_if_branch_event_trace=true;
[folder,~,~]=fileparts(output_path);
if ~isfolder(folder);mkdir(folder);end
report=struct();
report.schema=metadata.schema;
report.metadata=metadata;
report.native_history_finite_zero_based=(k(:)'-1);
report.native_history_x=double(native_iter.x(k,:));
report.native_history_val=double(v(k,:))';
report.direct_calls=direct;
report.first_original_reference_free_start=[-3,-6,3.871201010907891];
report.original_science='63/64 SCIENTIFIC NONPASS';
report.independent_review='NOT_RECEIVED';
report.perf01c='NOT_FROZEN';report.timing='NOT_RUN';
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:io','Cannot record actual direct optimizer calls');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
clear cleanup;
[raw_folder,~,~]=fileparts(raw_mat_path);
if ~isfolder(raw_folder);mkdir(raw_folder);end
save(raw_mat_path,'native_public','instrumented_public',...
     'native_iter','instrumented_iter','metadata','-v7');
if hook_count~=1 || ~delegated || ~neutral || ~history_equal || ...
   counts(1)~=1 || counts(2)<1 || counts(4)~=0
    error('hgfx:perf01:neutrality','Actual source objective call trace did not meet neutrality/inventory');
end
fprintf('Original MATLAB-owned direct source calls archived, no optimizer source changes; 63/64 science NONPASS\n');

    function optres=capture_and_delegate(obj,init,config)
        hook_count=hook_count+1;
        if ~isequal(init(:),[-3;-6;3.871201010907891]) || ...
           config.nRandInit~=0 || ~config.optIter
            error('hgfx:perf01:hook','Frozen original free start or optimizer history changed');
        end
        % Share the ACTUAL original private objective handle in parent scope.\n        % MATLAB sibling nested functions cannot access each other's locals.\n        obj_callback=obj;\n        optres=original(@logged_objective,init,config);
        captured_optim=optres;
        delegated=true;
    end

    function value=logged_objective(x)
        value=double(obj_callback(x));  % CALL THE EXACT PRIVATE MATLAB OBJECTIVE ONCE.
        total_calls=total_calls+1;
        stack=dbstack('-completenames');
        if numel(stack)<2 || ...
           ~strcmp(strrep(stack(2).file,'\','/'),strrep(q,'\','/')) || ...
           ~strcmp(stack(2).name,'quasinewton_optim')
            indirect_calls=indirect_calls+1;
            return
        end
        line=stack(2).line;
        if line==input_line(1)
            kind='INITIAL';counts(1)=counts(1)+1;
        elseif line==candidate_line
            kind='LINESEARCH';counts(2)=counts(2)+1;
        elseif line==input_line(2)
            kind='RESET';counts(3)=counts(3)+1;
        else
            kind='UNRECOGNIZED';counts(4)=counts(4)+1;
        end
        record=struct();
        record.call_number=double(total_calls);
        record.direct_index_zero_based=double(numel(direct));
        record.kind=kind;
        record.source_line=double(line);
        record.optimizer_name=stack(2).name;
        record.free_x=double(x(:))';
        record.private_objective=value;
        record.finite=isfinite(value);
        record.realmax_sentinel=(value==realmax);
        direct{end+1}=record;
    end
end
