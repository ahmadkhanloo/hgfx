function subject7_x0_matlab_infstates(root,toolbox_root,hgfx_report,hgfx_sha_sidecar,original_matlab_terms,output_file)
% Genuine original frozen MATLAB native HGF infStates and unitsq observation.
% Original fitModel/optimizer/observational source files never modified.
% All 71 native trial logp must EXACTLY match original source algebra archive.
% All original 71 objective values already separately genuine nested private.
addpath(genpath(toolbox_root));
hf='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
ml='2437f4dc241541072722a2695ddeca7b44d83dd3';
rootp=[strrep(toolbox_root,'\','/'),'/'];
required={which('fitModel'),which('hgf_binary'),which('unitsq_sgm')};
for j=1:numel(required)
    if isempty(required{j}) || ~startsWith(strrep(required{j},'\','/'),rootp)
        error('hgfx:perf01:source','Expected frozen reference function is not in original HGF toolbox');
    end
end
h=jsondecode(fileread(hgfx_report));
sha=lower(strtrim(fileread(hgfx_sha_sidecar)));
prev=jsondecode(fileread(original_matlab_terms));
if ~strcmp(h.schema,'perf01d-frozen-hgfx-infstates-71-native-obs-v1') || ...
   ~strcmp(h.status,'ORIGINAL_FROZEN_HGFX_INFSTATES_AND_UNITSQ_SOURCE_EXACT_ALL_71') || ...
   ~strcmp(h.frozen_hgfx_sha,hf) || ~strcmp(h.frozen_matlab_sha,ml) || ...
   ~strcmp(h.original_scientific_fitting,'63/64 SCIENTIFIC NONPASS') || ...
   h.original_failures.traj_mu~=4 || h.original_failures.traj_muhat~=4 || ...
   h.original_71_node_count~=71 || numel(h.nodes)~=71 || ...
   ~isequal(double(h.inf_states_shape_per_node(:)'),[128,3,4]) || ...
   h.predorpost~=1 || ...
   ~strcmp(h.independent_scientific_review,'NOT_RECEIVED') || ...
   ~strcmp(h.perf01c,'NOT_FROZEN') || ...
   numel(sha)~=64 || any(~ismember(sha,'0123456789abcdef')) || ...
   ~strcmp(prev.schema,'perf01d-matlab-objective-terms-71-v1') || ...
   ~strcmp(prev.original_scientific_fit,'63/64 SCIENTIFIC NONPASS') || ...
   numel(prev.nodes)~=71 || ...
   ~strcmp(prev.original_native_optimization,'UNMODIFIED_FROZEN_FITMODEL')
    error('hgfx:perf01:source','Original 71 node source or scientific failure provenance changed');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original binary 64x128 input changed');
end
u=double(data.u(8,:))';y=double(data.y(8,:))';
cfg=quasinewton_optim_config();
if cfg.nRandInit~=0 || cfg.maxIter~=100 || cfg.maxStep~=1 || ...
   cfg.maxRegu~=16 || cfg.maxRst~=10 || cfg.tolGrad~=1e-3 || ...
   cfg.tolArg~=1e-3 || ~cfg.optIter || cfg.verbose || ...
   ~strcmp(func2str(cfg.opt_algo),'quasinewton_optim')
    error('hgfx:perf01:fit','Original optimizer config unexpectedly differs');
end
native=[];
full_fit_text=evalc('native=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
if native.c_obs.predorpost~=1
    error('hgfx:perf01:obs','Frozen original unitsq observation selector must use predictions');
end
prc_fun=native.c_prc.prc_fun;
obs_fun=native.c_obs.obs_fun;
funcs={which(func2str(prc_fun)),which(func2str(obs_fun))};
for k=1:numel(funcs)
    if isempty(funcs{k}) || ~startsWith(strrep(funcs{k},'\','/'),rootp)
        error('hgfx:perf01:lineage','Original native model function resolved outside frozen source');
    end
end
mu=[native.c_prc.priormus,native.c_obs.priormus];
v=[native.c_prc.priorsas,native.c_obs.priorsas];
v(isnan(v))=0;indices=find(v);
if ~isequal(indices(:)',[13,14,15]) || ...
   ~isequal(double(mu(indices)),[-3,-6,3.871201010907891])
    error('hgfx:perf01:free','Original optimized free parameters/start changed');
end
nprc=numel(native.c_prc.priormus);
nobs=numel(native.c_obs.priormus);
rows=cell(1,0);
for i=1:71
    src=h.nodes(i);old=prev.nodes(i);
    x=double(src.x(:))';
    xhex=cellstr(num2hex(x(:)));
    archived=cellstr(string(src.x_hex(:)));
    if src.ordinal~=i-1 || old.original_node_index~=i-1 || ...
       ~isequal(xhex(:),archived(:)) || ...
       ~isequal(xhex(:),cellstr(string(old.x_hex(:)))) || ...
       ~all(isfinite(x))
        error('hgfx:perf01:sourcex','Original 71 x0 source nodes are not bitwise identical');
    end
    full=mu;full(indices)=x;
    pt=full(1:nprc);
    ot=full(nprc+1:nprc+nobs);
    [~,inferred]=prc_fun(native,pt,'trans');
    if ~isequal(size(inferred),[128,3,4])
        error('hgfx:perf01:infstate','Original HGF infStates source dimensions changed');
    end
    predictor=inferred(:,1,1);
    posterior=inferred(:,1,3);
    if ~all(isfinite(predictor)) || ~all(isfinite(posterior))
        error('hgfx:perf01:infstate','Original selected predictor/posterior not finite');
    end
    [native_logp,~,~]=obs_fun(native,inferred,ot);
    native_logp=double(native_logp(:));
    source_logp=double(old.components.full_trial_log_likelihood(:));
    if numel(native_logp)~=128 || numel(source_logp)~=128 || ...
       ~all(isfinite(native_logp)) || ...
       ~all(strcmp(cellstr(num2hex(native_logp)),cellstr(num2hex(source_logp))))
        error('hgfx:perf01:original','Unmodified original native MATLAB HGF+unitsq trial logp NOT exact at source node %d',i-1);
    end
    % Counterfactual source observation: change ONLY selected predictor.
    % This must NEVER overwrite original genuine MATLAB objective/LL.
    hpred=double(src.native_prediction_level1(:));
    if numel(hpred)~=128 || ~all(isfinite(hpred))
        error('hgfx:perf01:hgfxinput','Original frozen HGFX source predictor invalid');
    end
    cross=inferred;
    cross(:,1,1)=hpred;
    matlab_unitsq_on_hgfx_prediction=obs_fun(native,cross,ot);
    matlab_unitsq_on_hgfx_prediction=double(matlab_unitsq_on_hgfx_prediction(:));
    if numel(matlab_unitsq_on_hgfx_prediction)~=128 || ...
       ~all(isfinite(matlab_unitsq_on_hgfx_prediction))
        error('hgfx:perf01:swap','Frozen MATLAB unitsq on genuine HGFX same-x prediction failed');
    end
    state=struct();
    state.muhat=inferred(:,:,1);
    state.sahat=inferred(:,:,2);
    state.mu=inferred(:,:,3);
    state.sa=inferred(:,:,4);
    row=struct();
    row.ordinal=i-1;row.x=x;row.x_hex=xhex';
    row.original_genuine_private_objective=double(old.original_matlab_private_source_scalar);
    row.original_hgfx_objective=double(src.native_source_objective);
    row.native_logp=native_logp';
    row.native_prediction_level1=predictor';
    row.native_posterior_level1=posterior';
    row.native_zeta=exp(ot(1));
    row.native_inf_states=state;
    row.matlab_unitsq_on_hgfx_prediction_logp=matlab_unitsq_on_hgfx_prediction';
    rows{end+1}=row;
end
out=struct();
out.schema='perf01d-frozen-matlab-infstates-71-native-and-cross-obs-v1';
out.status='ORIGINAL_FROZEN_MATLAB_INFSTATES_NATIVE_EXACT_AND_OBS_ON_HGFX';
out.frozen_hgfx_sha=hf;out.frozen_matlab_sha=ml;
out.original_hgfx_infstates_sha256=sha;
out.original_true_private_ridders_run='42389292284';
out.original_true_private_ridders_sha='4ab5f42754b1200433d9b7dc6832e1ee7c45be8f';
out.original_constituents_source_run='42402421462';
out.original_scientific_fitting='63/64 SCIENTIFIC NONPASS';
out.original_failures=struct('traj_mu',4,'traj_muhat',4);
out.original_71_node_count=numel(rows);
out.n_trials=128;out.inf_states_shape_per_node=[128,3,4];
out.predorpost=1;
out.native_fit_unmodified=true;
out.native_fit_log_characters=numel(full_fit_text);
out.native_perceptual_function=func2str(prc_fun);
out.native_observation_function=func2str(obs_fun);
out.native_perceptual_file=funcs{1};
out.native_observation_file=funcs{2};
out.native_fitmodel_file=which('fitModel');
out.nodes=rows;
out.github_run_id=getenv('GITHUB_RUN_ID');
out.tested_sha=getenv('GITHUB_SHA');
out.matlab_version=version;
out.matlab_release=version('-release');
out.independent_scientific_review='NOT_RECEIVED';
out.perf01c='NOT_FROZEN';
out.paper_timing='NOT_RUN';
out.physical_gpu='NOT_RUN';
[folder,~,~]=fileparts(output_file);
if ~isfolder(folder);mkdir(folder);end
fid=fopen(output_file,'w');
if fid<0;error('hgfx:perf01:io','Cannot save original MATLAB infStates source archive');end
clean=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
clear clean;
fprintf('Original frozen MATLAB HGF 71/71 native per-trial LL EXACT; original 63/64 SCIENTIFIC NONPASS\n');
end
