function run_rev22_d08_matlab(output_path, cache_path)
% REV-2.2 official D08: ONE unchanged MATLAB simulator + ONE exact default fit.
% New science from preregistered 2026-11-11 protocol. Not historical replay.
assert(~exist(output_path,'file') && ~exist(cache_path,'file'), 'REV22:overwrite');
root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
toolbox=fullfile(root,'external','hgf-toolbox');
[rc,sha]=system(sprintf('git -C "%s" rev-parse HEAD',toolbox));
assert(rc==0 && strcmp(strtrim(sha), ...
 '2437f4dc241541072722a2695ddeca7b44d83dd3'),'REV22:referenceDrift');
[rc,blob]=system(sprintf('git -C "%s" hash-object demo/example_usdchf.txt',toolbox));
assert(rc==0 && strcmp(strtrim(blob), ...
 '29a4d0322faf8894c414883c517950aa87b481db'),'REV22:inputSourceDrift');
addpath(genpath(toolbox));
addpath(fullfile(root,'reference','matlab','m11_shims'));
x=load(fullfile(toolbox,'demo','example_usdchf.txt'));
assert(isvector(x) && numel(x)==614 && all(isfinite(x(:))), ...
    'REV22:inputLengthOrNonfinite');
native=[1.04 1 .0001 .1 0 0 1 -13 -2 1e4];
obs_native=.00002;seed=123456789;
lastwarn('','');
s=simModel(x,'uhgf',native,'gaussian_obs',obs_native,seed);
assert(numel(s.y)==614 && all(isfinite(s.y(:))),'REV22:responseLength');
% The authentic official D08 fit; NO optimizer or prior substitutions.
lastwarn('','');
r=fitModel(s.y,x,uhgf_config(),gaussian_obs_config(), ...
    'quasinewton_optim_config');
[last_warning,last_warning_id]=lastwarn;
assert(strcmp(r.c_prc.model,'uhgf') || strcmp(r.c_prc.model,'uHGF') ...
    || isfield(r.c_prc,'prc_fun'),'REV22:missingPrc');
assert(numel(r.optim.final)==numel(r.c_prc.priormus)+numel(r.c_obs.priormus), ...
    'REV22:endpointLength');
v.protocol='compstat-rev2-2-d08-original-oracle-v1';
v.source='matlab';v.reference_commit= ...
  '2437f4dc241541072722a2695ddeca7b44d83dd3';
v.release_source_commit='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
v.matlab_version=version;
v.model='uhgf';v.observation_model='gaussian_obs';
v.seed=seed;v.inputs=x;v.responses=s.y;
v.native_simulation=native;v.native_observation=obs_native;
v.trials=614;v.inputs_source_git_blob= ...
 '29a4d0322faf8894c414883c517950aa87b481db';
v.final=r.optim.final;v.init=r.optim.init;
v.native_fit_perceptual=r.p_prc.p;
v.native_fit_observation=r.p_obs.p;
v.prior_means=[r.c_prc.priormus,r.c_obs.priormus];
v.prior_variances=[r.c_prc.priorsas,r.c_obs.priorsas];
v.free_indices_matlab=find(~isnan(v.prior_variances) & v.prior_variances~=0);
v.negLl=r.optim.negLl;v.negLj=r.optim.negLj;
v.BIC=r.optim.BIC;v.LME=r.optim.LME;
v.H=r.optim.H;v.Sigma=r.optim.Sigma;v.Corr=r.optim.Corr;
v.traj=r.traj;v.yhat=r.optim.yhat;v.res=r.optim.res;
v.termination='NOT_EXPORTED';
v.converged='NOT_EXPORTED';
v.last_warning_only.message=last_warning;
v.last_warning_only.identifier=last_warning_id;
v.warning_coverage='WARNING_COVERAGE_INCOMPLETE';
v.full_warning_count='NOT_CAPTURED';
v.science_claim='NOT_CLASSIFIED_UNTIL_PAIRED';
if isstruct(r.optim.iter)
  v.iter.x=r.optim.iter.x;
  v.iter.val=r.optim.iter.val;
  v.iter.rst=r.optim.iter.rst;
else
  v.iter=struct('present',false);
end
folder=fileparts(output_path);
if ~isempty(folder)&&~exist(folder,'dir');mkdir(folder);end
fid=fopen(output_path,'w');assert(fid>=0,'REV22:write');
clean=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(v),'PrettyPrint',true));
clear clean;
% Preserve full original MATLAB context to evaluate HGFX endpoint WITHOUT
% running MATLAB fitModel a second time.
save(cache_path,'r','x','s','-v7');
fprintf('REV22 D08 MATLAB official one fit exported; NO PARITY PASS.\n');
end
