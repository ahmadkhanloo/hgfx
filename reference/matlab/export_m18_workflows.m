function export_m18_workflows(output_path)
% Frozen official demo workflow contracts; no fitted-data-dependent selection.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));
u = load(fullfile(root,'external','hgf-toolbox','demo','example_binary_input.txt'));
x = load(fullfile(root,'external','hgf-toolbox','demo','example_usdchf.txt'));
meta.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
meta.numeric_encoding = 'ieee-strings-v1';
meta.matlab_version = version;
meta.protocol = 'official-demo-workflows-1';
meta.bernoulli_driver = 'M11 Bernoulli shim; exported uniforms, not Statistics Toolbox RNG identity';
payload.metadata = meta;
binary = [NaN 0 1 NaN 1 1 NaN 0 0 1 1 NaN -2.5 -6];
continuous = [1.04 1 .0001 .1 0 0 1 -13 -2 1e4];
specs = {
 'D01_bayes',u,'hgf_binary','bayes_optimal_binary',[],[],1;
 'D01_fit',u,'hgf_binary','unitsq_sgm',binary,5,1;
 'D02_fit',u,'ehgf_binary','unitsq_sgm',[NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3],5,.5;
 'D03_fit',u,'uhgf_binary','unitsq_sgm',binary,5,.5;
 'D05_fit',u,'rw_binary','unitsq_sgm',binary,5,1;
 'D06_bayes',x,'hgf','bayes_optimal',[],[],1;
 'D06_fit',x,'hgf','gaussian_obs',continuous,.00002,1;
 'D07_fit',x,'ehgf','gaussian_obs',continuous,.00002,1;
 'D08_fit',x,'uhgf','gaussian_obs',continuous,.00002,1
};
payload.cases = cell(1,size(specs,1));
for k=1:size(specs,1)
 c.id=specs{k,1}; c.inputs=specs{k,2}; c.model=specs{k,3};
 c.observation=specs{k,4}; c.native=specs{k,5}; c.obs_native=specs{k,6};
 c.obs_prior_variance=specs{k,7}; c.seed=123456789;
 c.success=false; c.stage='simulation'; c.error_identifier=''; c.error_message='';
 c.sim=struct; c.fit=struct; c.responses=[]; c.driver=[];
 try
   if isempty(c.native)
     y=[];
   else
     generator=c.model;
     if strcmp(c.id,'D05_fit'); generator='hgf_binary'; end
     s=simModel(c.inputs,generator,c.native,c.observation,c.obs_native,c.seed);
     c.sim=strip_sim(s); y=s.y;
     rng(c.seed);
     if strcmp(c.observation,'gaussian_obs'); c.driver=randn(length(y),1);
     else; c.driver=rand(length(y),1); end
   end
   c.responses=y; c.stage='fit';
   pc=feval([c.model,'_config']); oc=feval([c.observation,'_config']);
   if strcmp(c.observation,'unitsq_sgm')
     oc.logzesa=c.obs_prior_variance; oc=align_priors(oc);
   end
   fit=fitModel(y,c.inputs,pc,oc,'quasinewton_optim_config');
   c.fit=strip_fit(fit); c.success=true; c.stage='complete';
 catch ME
   c.error_identifier=ME.identifier; c.error_message=ME.message;
 end
 payload.cases{k}=c;
 write_payload(output_path,payload);
 fprintf('M18 workflow %s: success=%d stage=%s\n',c.id,c.success,c.stage);
end
end

function out=strip_sim(s)
out.y=s.y; out.traj=s.traj; out.p_prc=s.p_prc.p; out.p_obs=s.p_obs.p;
if isfield(s,'yhat'); out.yhat=s.yhat; end
end

function out=strip_fit(s)
out.final=s.optim.final; out.traj=s.traj; out.p_prc=s.p_prc.p;
out.p_obs=s.p_obs.p; out.prc_priormus=s.c_prc.priormus;
out.prc_priorsas=s.c_prc.priorsas; out.obs_priormus=s.c_obs.priormus;
out.obs_priorsas=s.c_obs.priorsas;
fields={'H','Sigma','Corr','negLl','negLj','LME','AIC','BIC','yhat','res','resAC'};
for j=1:numel(fields); out.(fields{j})=s.optim.(fields{j}); end
end

function write_payload(path,payload)
folder=fileparts(path); if ~exist(folder,'dir'); mkdir(folder); end
fid=fopen(path,'w'); assert(fid>=0); cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
end
