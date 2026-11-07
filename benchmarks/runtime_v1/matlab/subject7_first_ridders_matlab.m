function subject7_first_ridders_matlab(root,toolbox_root,hgfx_source_path,hgfx_sha_path,output_path,raw_mat_path)
% AUTHOR-SIDE: ORIGINAL MATLAB private fitModel objective and original Ridders.
% Frozen MATLAB Ridders/optimizer files are NEVER edited or intercepted.
% Native and diagnostics+delegated public fits must match exactly.
addpath(genpath(toolbox_root));
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
hf='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
prefix=[strrep(toolbox_root,'\','/'),'/'];
source_files={which('fitModel'),which('quasinewton_optim'),...
              which('riddersgradient'),which('riddersdiff')};
for idx=1:numel(source_files)
    if ~startsWith(strrep(source_files{idx},'\','/'),prefix)
        error('hgfx:perf01:source','Frozen original MATLAB path does not resolve');
    end
end
source=jsondecode(fileread(hgfx_source_path));
if ~strcmp(source.schema,'perf01d-initial-real-ridders-3coord-v1') || ...
   ~strcmp(source.status,'SOURCE_HGFX_INITIAL_RIDDERS_OWN_STENCIL') || ...
   ~strcmp(source.frozen_hgfx_sha,hf) || ~strcmp(source.frozen_matlab_sha,ref) || ...
   ~strcmp(source.original_63_subject_fit_status,'63/64 SCIENTIFIC NONPASS') || ...
   source.min_steps~=10 || source.max_steps~=100 || ...
   source.init_h~=1 || source.div~=1.2 || source.tf~=2 || ...
   numel(source.hgfx_nodes)<67 || ...
   ~isequal(double(source.x0(:)'),[-3,-6,3.871201010907891])
    error('hgfx:perf01:prespec','Frozen original HGFX x0 stencil protocol changed');
end
sha=lower(strtrim(fileread(hgfx_sha_path)));
if numel(sha)~=64 || any(~ismember(sha,'0123456789abcdef'))
    error('hgfx:perf01:sha','SHA256 source sidecar malformed');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original 64 by 128 dataset changed');
end
u=double(data.u(8,:))';y=double(data.y(8,:))';
cfg=quasinewton_optim_config();
original=cfg.opt_algo;
if ~strcmp(func2str(original),'quasinewton_optim') || ...
   cfg.nRandInit~=0 || cfg.maxIter~=100 || cfg.maxStep~=1 || ...
   cfg.maxRegu~=16 || cfg.maxRst~=10 || cfg.tolGrad~=1e-3 || ...
   cfg.tolArg~=1e-3 || ~cfg.optIter || cfg.verbose
    error('hgfx:perf01:config','Original MATLAB BFGS config changed');
end

native=[];wrapped=[];obj_callback=[];hook_count=0;delegated=false;
matlab_nodes=cell(1,0);hgfx_cross=cell(1,0);
matlab_gradient=[];matlab_error=[];
native_console=evalc('native=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
cfg.opt_algo=@diagnose_then_delegate;
wrapped_console=evalc('wrapped=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');

opt_names={'init','final','H','Sigma','Corr','trialLogLlsplit',...
           'negLl','negLj','LME','decompLME','AIC','BIC','yhat','res','resAC'};
traj_names=fieldnames(native.traj);
neutral=numel(traj_names)==11 && numel(fieldnames(wrapped.traj))==11;
for k=1:numel(opt_names)
    name=opt_names{k};
    neutral=neutral && isfield(native.optim,name) && ...
       isfield(wrapped.optim,name) && ...
       isequaln(native.optim.(name),wrapped.optim.(name));
end
for k=1:numel(traj_names)
    name=traj_names{k};
    neutral=neutral && isfield(wrapped.traj,name) && ...
       isequaln(native.traj.(name),wrapped.traj.(name));
end
iter_equal=isfield(native.optim,'iter') && ...
           isfield(wrapped.optim,'iter') && ...
           isequaln(native.optim.iter,wrapped.optim.iter);
if ~neutral || ~iter_equal || hook_count~=1 || ~delegated || ...
   numel(matlab_gradient)~=3 || numel(matlab_error)~=3 || ...
   ~all(isfinite(matlab_gradient)) || ~all(isfinite(matlab_error)) || ...
   numel(hgfx_cross)~=numel(source.hgfx_nodes) || ...
   numel(matlab_nodes)<67 || mod(numel(matlab_nodes)-1,2)~=0
    error('hgfx:perf01:neutrality','Native MATLAB fitting changed or genuine Ridders source incomplete');
end
vv=native.optim.iter.val;
if numel(find(isfinite(vv)))~=25 || ...
   ~isequal(size(native.optim.iter.x),[101,3])
    error('hgfx:perf01:history','Original 25-row public optimizer state changed');
end
native_public=struct('optim',struct(),'traj',struct());
instrumented_public=struct('optim',struct(),'traj',struct());
for k=1:numel(opt_names)
    name=opt_names{k};
    native_public.optim.(name)=native.optim.(name);
    instrumented_public.optim.(name)=wrapped.optim.(name);
end
for k=1:numel(traj_names)
    name=traj_names{k};
    native_public.traj.(name)=native.traj.(name);
    instrumented_public.traj.(name)=wrapped.traj.(name);
end
native_iter=native.optim.iter;
instrumented_iter=wrapped.optim.iter;
metadata=struct();
metadata.schema='perf01d-real-private-matlab-first-ridders-stencil-v1';
metadata.frozen_hgfx_sha=hf;
metadata.frozen_matlab_sha=ref;
metadata.source_hgfx_stencil_sha256=sha;
metadata.original_science='63/64 SCIENTIFIC NONPASS';
metadata.independent_review='NOT_RECEIVED';
metadata.perf01c='NOT_FROZEN';
metadata.timing='NOT_RUN';metadata.hook_count=hook_count;
metadata.delegated=delegated;metadata.subject_index_zero_based=7;
metadata.trials=128;metadata.min_steps=10;
metadata.opt_fields=opt_names;metadata.traj_fields=traj_names;
metadata.native_wrapped_26_and_iter_exact=neutral && iter_equal;
metadata.github_run_id=getenv('GITHUB_RUN_ID');
metadata.tested_sha=getenv('GITHUB_SHA');
metadata.matlab_version=version;metadata.matlab_release=version('-release');
metadata.native_console_characters=numel(native_console);
metadata.instrumented_console_characters=numel(wrapped_console);

[mat_folder,~,~]=fileparts(raw_mat_path);
if ~isfolder(mat_folder);mkdir(mat_folder);end
save(raw_mat_path,'native_public','instrumented_public',...
    'native_iter','instrumented_iter','metadata','-v7');
out=struct();
out.schema=metadata.schema;
out.frozen_hgfx_sha=hf;out.frozen_matlab_sha=ref;
out.source_hgfx_stencil_sha256=sha;
out.original_science='63/64 SCIENTIFIC NONPASS';
out.original_failure=struct('traj_mu',4,'traj_muhat',4);
out.github_run_id=getenv('GITHUB_RUN_ID');
out.tested_sha=getenv('GITHUB_SHA');
out.hook_count=hook_count;out.original_optimizer_delegated=delegated;
out.native_wrapped_26_and_iter_exact=neutral && iter_equal;
out.min_steps=10;out.x0_hex=cellstr(num2hex([-3;-6;3.871201010907891]))';
out.matlab_gradient=double(matlab_gradient(:))';
out.matlab_error=double(matlab_error(:))';
out.matlab_nodes=matlab_nodes;
out.matlab_on_hgfx_nodes=hgfx_cross;
out.matlab_version=version;out.matlab_release=version('-release');
out.independent_review='NOT_RECEIVED';
out.perf01c='NOT_FROZEN';out.timing='NOT_RUN';out.gpu='NOT_RUN';
[folder,~,~]=fileparts(output_path);
if ~isfolder(folder);mkdir(folder);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:io','Cannot archive genuine private MATLAB stencil');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
clear cleanup;
fprintf('Original MATLAB private Ridders x0 stencil and HGFX same-x cross evaluations saved, scientific 63/64 NONPASS\n');

    function optresult=diagnose_then_delegate(obj,init,config)
        hook_count=hook_count+1;
        if ~isequal(init(:),[-3;-6;3.871201010907891]) || ...
           config.nRandInit~=0 || ~config.optIter
            error('hgfx:perf01:start','Private MATLAB fitModel free start/config changed');
        end
        obj_callback=obj;
        rr=struct('min_steps',10);
        [matlab_gradient,matlab_error]=riddersgradient(@logged_obj,init,rr);
        for t=1:numel(source.hgfx_nodes)
            item=source.hgfx_nodes(t);
            x=double(item.x(:));
            if numel(x)~=3 || ~all(isfinite(x))
                error('hgfx:perf01:x','Transported original HGFX stencil coordinate missing');
            end
            value=double(obj(x));
            if ~isscalar(value) || ~isfinite(value)
                error('hgfx:perf01:scalar','Real private MATLAB objective nonfinite on HGFX node');
            end
            record=struct();
            record.ordinal=t-1;
            record.x=x';
            record.value=value;
            hgfx_cross{end+1}=record;
        end
        optresult=original(obj,init,config);
        delegated=true;
    end

    function value=logged_obj(x)
        value=double(obj_callback(x));
        if ~isscalar(value) || ~isfinite(value)
            error('hgfx:perf01:scalar','Original Ridders objective nonfinite');
        end
        a=double(x(:))';
        record=struct('ordinal',numel(matlab_nodes),...
                      'x',a,'value',value,...
                      'x_hex',{cellstr(num2hex(a(:)))'});
        matlab_nodes{end+1}=record;
    end
end
