function subject7_x0_matlab_objective_components(root,toolbox_root,hgfx_report,sha_sidecar,output_path)
% Author-side source-algebra replica for constituent attribution only.
% Frozen fitModel.m, HGF model, obs model and optimizer NOT modified.
% Every final scalar must match 71 original actual private callback values
% from run 42389292284 EXACTLY or the whole experiment is invalid.
addpath(genpath(toolbox_root));
hf='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
ml='2437f4dc241541072722a2695ddeca7b44d83dd3';
prefix=[strrep(toolbox_root,'\','/'),'/'];
cfg_files={which('fitModel'),which('hgf_binary'),which('unitsq_sgm')};
for j=1:numel(cfg_files)
    if isempty(cfg_files{j}) || ~startsWith(strrep(cfg_files{j},'\','/'),prefix)
        error('hgfx:perf01:source','Frozen MATLAB source function not located in original toolbox');
    end
end
report=jsondecode(fileread(hgfx_report));
sha=lower(strtrim(fileread(sha_sidecar)));
if ~strcmp(report.schema,'perf01d-objective-term-decomp-genuine-source-71-v1') || ...
   ~strcmp(report.status,'AUTHOR_SIDE_FROZEN_HGFX_71_SOURCE_TERM_DECOMPOSITION') || ...
   ~strcmp(report.frozen_hgfx_sha,hf) || ~strcmp(report.frozen_matlab_sha,ml) || ...
   ~strcmp(report.original_scientific_fit,'63/64 SCIENTIFIC NONPASS') || ...
   ~strcmp(report.independent_scientific_review,'NOT_RECEIVED') || ...
   ~strcmp(report.perf01c,'NOT_FROZEN') || ...
   report.original_71_source_node_count~=71 || numel(report.nodes)~=71 || ...
   numel(sha)~=64 || any(~ismember(sha,'0123456789abcdef'))
    error('hgfx:perf01:archive','Untrusted frozen original Python source archive');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.y),[64,128]) || ~isequal(size(data.u),[64,128])
    error('hgfx:perf01:data','Original 64x128 failed cohort modified');
end
u=double(data.u(8,:))';
y=double(data.y(8,:))';
cfg=quasinewton_optim_config();
if cfg.nRandInit~=0 || cfg.maxIter~=100 || ~cfg.optIter || ...
   ~strcmp(func2str(cfg.opt_algo),'quasinewton_optim')
    error('hgfx:perf01:optimizer','Original frozen optimizer config was altered');
end
% Call original native fitModel exactly as published; no objective wrapper.
native=[];
native_console=evalc('native=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
prc_fun=native.c_prc.prc_fun;
obs_fun=native.c_obs.obs_fun;
funcs={which(func2str(prc_fun)),which(func2str(obs_fun))};
for j=1:numel(funcs)
    if isempty(funcs{j}) || ~startsWith(strrep(funcs{j},'\','/'),prefix)
        error('hgfx:perf01:model','Actual native model source not frozen');
    end
end
prior_means=[native.c_prc.priormus,native.c_obs.priormus];
prior_var=[native.c_prc.priorsas,native.c_obs.priorsas];
all_idx=prior_var;
all_idx(isnan(all_idx))=0;
all_idx=find(all_idx);
if ~isequal(all_idx(:)',[13,14,15]) || ...
   ~isequal(double(prior_means(all_idx)),[-3,-6,3.871201010907891])
    error('hgfx:perf01:free','Original free index/start changed');
end
n_prc=length(native.c_prc.priormus);
n_obs=length(native.c_obs.priormus);
pidx=native.c_prc.priorsas;
pidx(isnan(pidx))=0;pidx=find(pidx);
oidx=native.c_obs.priorsas;
oidx(isnan(oidx))=0;oidx=find(oidx);
nodes=cell(1,0);
for i=1:71
    src=report.nodes(i);
    x=double(src.x(:))';
    expected=cellstr(num2hex(x(:)));
    recorded=cellstr(string(src.x_hex(:)));
    if numel(x)~=3 || ~all(isfinite(x)) || ...
       ~isequal(expected(:),recorded(:)) || ...
       ~isequal(double(src.x(:))',x)
        error('hgfx:perf01:coordinate','Original source coordinate altered in JSON transport');
    end
    full=prior_means;
    full(all_idx)=x;
    pt=full(1:n_prc);
    ot=full(n_prc+1:n_prc+n_obs);
    % Exact algebra and source operation order from FROZEN fitModel.m
    [~,infStates]=prc_fun(native,pt,'trans');
    try
        [trialLogLls,~,~,~]=obs_fun(native,infStates,ot);
    catch
        trialLogLls=obs_fun(native,infStates,ot);
    end
    trialLogLls=double(trialLogLls(:));
    if numel(trialLogLls)~=128 || ~all(isfinite(trialLogLls))
        error('hgfx:perf01:trials','Original observation model did not return 128 finite trials');
    end
    regular=trialLogLls;
    regular(native.irr)=[];
    logLl=sum(regular);
    negLl=-logLl;
    prc_terms= -1/2.*log(8*atan(1).*native.c_prc.priorsas(pidx)) ...
               -1/2.*(pt(pidx)-native.c_prc.priormus(pidx)).^2./native.c_prc.priorsas(pidx);
    prc_total=sum(prc_terms);
    obs_terms= -1/2.*log(8*atan(1).*native.c_obs.priorsas(oidx)) ...
               -1/2.*(ot(oidx)-native.c_obs.priormus(oidx)).^2./native.c_obs.priorsas(oidx);
    obs_total=sum(obs_terms);
    negJoint=-(logLl+prc_total+obs_total);
    original_matlab_private=double(src.original_matlab_private_source_scalar);
    if ~isscalar(negJoint) || ~isfinite(negJoint) || ...
       ~strcmp(num2hex(negJoint),num2hex(original_matlab_private))
        error('hgfx:perf01:reconstruction',...
              'MATLAB source constituent reconstruction NOT EXACT at original private source index %d',i-1);
    end
    record=struct();
    record.original_node_index=i-1;
    record.x=x;record.x_hex=expected';
    record.original_matlab_private_source_scalar=original_matlab_private;
    record.original_hgfx_source_scalar=double(src.original_hgfx_source_scalar);
    component=struct();
    component.full_trial_log_likelihood=trialLogLls';
    mask=true(1,128);mask(native.irr)=false;
    component.regular_trial_mask=mask;
    component.log_likelihood=logLl;
    component.negative_log_likelihood=negLl;
    component.perceptual_prior_terms=prc_terms;
    component.perceptual_prior_log_total=prc_total;
    component.observation_prior_terms=obs_terms;
    component.observation_prior_log_total=obs_total;
    component.negative_log_joint=negJoint;
    record.components=component;
    nodes{end+1}=record;
end
out=struct();
out.schema='perf01d-matlab-objective-terms-71-v1';
out.status='AUTHOR_SIDE_REAL_FROZEN_MATLAB_MODEL_SOURCE_CONSTITUENTS';
out.original_hgfx_component_sha256=sha;
out.source_original_real_run='42389292284';
out.source_original_real_sha='4ab5f42754b1200433d9b7dc6832e1ee7c45be8f';
out.frozen_hgfx_sha=hf;out.frozen_matlab_sha=ml;
out.subject_index_zero_based=7;out.n_trials=128;
out.original_scientific_fit='63/64 SCIENTIFIC NONPASS';
out.original_failure=struct('traj_mu',4,'traj_muhat',4);
out.original_native_optimization='UNMODIFIED_FROZEN_FITMODEL';
out.original_native_fit_log_characters=numel(native_console);
out.native_perceptual_function=func2str(prc_fun);
out.native_observation_function=func2str(obs_fun);
out.perceptual_source_file=funcs{1};
out.observation_source_file=funcs{2};
out.negative_log_joint_source_file=which('fitModel');
out.original_71_source_node_count=numel(nodes);
out.nodes=nodes;
out.github_run_id=getenv('GITHUB_RUN_ID');
out.tested_sha=getenv('GITHUB_SHA');
out.matlab_version=version;
out.matlab_release=version('-release');
out.independent_review='NOT_RECEIVED';out.perf01c='NOT_FROZEN';
out.paper_timing='NOT_RUN';out.physical_gpu='NOT_RUN';
[folder,~,~]=fileparts(output_path);
if ~isfolder(folder);mkdir(folder);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:io','Could not create complete real MATLAB component archive');end
close_file=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
clear close_file;
fprintf('Original MATLAB native fitModel source-algebra 71/71 private objective terms EXACT; original 63/64 SCIENTIFIC NONPASS\n');
end
