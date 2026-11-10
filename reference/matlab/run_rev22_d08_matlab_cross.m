function run_rev22_d08_matlab_cross(cache_path, hgfx_path, output_path)
% REV-2.2 paired oracle objective at BOTH frozen endpoints, no second fit.
assert(~exist(output_path,'file'), 'REV22:overwrite');
assert(exist(cache_path,'file')==2 && exist(hgfx_path,'file')==2, ...
    'REV22:requiredInputsAbsent');
root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
load(cache_path,'r','x','s');
dev=jsondecode(fileread(hgfx_path));
assert(strcmp(char(dev.protocol),'compstat-rev2-2-d08-original-oracle-v1') ...
    && strcmp(char(dev.source),'hgfx') ...
    && dev.seed==123456789 && dev.trials==614 ...
    && strcmp(char(dev.model),'uhgf') ...
    && strcmp(char(dev.observation_model),'gaussian_obs'), ...
    'REV22:otherModelOrInputs');
assert(isequal(size(x(:)),size(s.y(:))) && numel(s.y)==614);
full=double(dev.final(:)');
assert(numel(full)==numel(r.optim.final) && all(isfinite(full)), ...
    'REV22:invalidHGFXEndpoint');
m=double(r.optim.final(:)');
ref=rev22_objective_at_endpoint(r,m);
other=rev22_objective_at_endpoint(r,full);
v.protocol='compstat-rev2-2-d08-original-oracle-v1';
v.source='matlab_cross';
v.model='uhgf';v.observation_model='gaussian_obs';v.seed=123456789;
v.trials=614;v.reference_commit= ...
  '2437f4dc241541072722a2695ddeca7b44d83dd3';
v.matlab_version=version;
v.matlab_endpoint=ref;
v.hgfx_endpoint=other;
v.matlab_original_negLj=r.optim.negLj;
v.matlab_original_negLl=r.optim.negLl;
v.self_evaluation_difference_negLj=ref.negLj-r.optim.negLj;
v.self_evaluation_difference_negLl=ref.negLl-r.optim.negLl;
v.original_matlab_fit_rerun=false;
v.scientific_gate='NOT_CLASSIFIED_NO_FAMILY_CROSS_GATE';
folder=fileparts(output_path);
if ~isempty(folder)&&~exist(folder,'dir');mkdir(folder);end
fid=fopen(output_path,'w');assert(fid>=0,'REV22:write');
clean=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(v),'PrettyPrint',true));
fprintf('REV22 D08 exact MATLAB endpoint cross-eval exported; NO FIT REPLAY.\n');
end

function out=rev22_objective_at_endpoint(r,full)
% Explicit local copy of frozen fitModel.m negLogJoint source expression,
% source contract asserted before science; do not change reduction/priors.
n_prc=numel(r.c_prc.priormus);
ptrans_prc=full(1:n_prc);
ptrans_obs=full(n_prc+1:end);
try
 [traj,infStates]=r.c_prc.prc_fun(r,ptrans_prc,'trans');
catch ME
 out.valid=false;out.error=['PRC: ' ME.identifier ' ' ME.message];
 out.negLj=realmax;out.negLl=realmax;out.trialLogLls=[];
 return;
end
try
 [trialLogLls,yhat,res,split]=r.c_obs.obs_fun(r,infStates,ptrans_obs);
catch
 [trialLogLls,yhat,res]=r.c_obs.obs_fun(r,infStates,ptrans_obs);
 split=trialLogLls;
end
regular=trialLogLls;
regular(r.irr)=[];
logLl=sum(regular);
if isnan(logLl);negLl=realmax;else;negLl=-logLl;end
prc_idx=r.c_prc.priorsas;
prc_idx(isnan(prc_idx))=0;prc_idx=find(prc_idx);
logPrc=-1/2.*log(8*atan(1).*r.c_prc.priorsas(prc_idx)) ...
  -1/2.*(ptrans_prc(prc_idx)-r.c_prc.priormus(prc_idx)).^2 ...
  ./r.c_prc.priorsas(prc_idx);
obs_idx=r.c_obs.priorsas;
obs_idx(isnan(obs_idx))=0;obs_idx=find(obs_idx);
logObs=-1/2.*log(8*atan(1).*r.c_obs.priorsas(obs_idx)) ...
  -1/2.*(ptrans_obs(obs_idx)-r.c_obs.priormus(obs_idx)).^2 ...
  ./r.c_obs.priorsas(obs_idx);
out.valid=all(isfinite(regular)) && isfinite(logLl);
out.error='';
out.negLl=negLl;
out.negLj=-(logLl+sum(logPrc)+sum(logObs));
out.perceptual_prior_total=sum(logPrc);
out.observation_prior_total=sum(logObs);
out.log_likelihood=logLl;
out.trialLogLls=trialLogLls;
out.traj=traj;
out.yhat=yhat;
out.res=res;
out.free_indices_matlab=[prc_idx,n_prc+obs_idx];
end
