function bfgs_state_subject7_matlab(root,toolbox_root,original,output_path)
% Untimed original subject-7 PUBLIC fitModel trace; no source modifications.
% This experiment is distinct from archived 64-subject run 41863441006.
addpath(genpath(toolbox_root));
hgfx='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
src=jsondecode(fileread(fullfile(original,'summary-41863441006.json')));
if ~strcmp(src.hgfx_sha,hgfx) || ~strcmp(src.matlab_sha,ref)
    error('hgfx:perf01:identity','Wrong original fit source SHAs');
end
raw=jsondecode(fileread(fullfile(original,'matlab_raw.json')));
old=raw.cases(8);
if old.subject_index_zero_based~=7 || ...
   ~strcmp(old.status,'MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION')
    error('hgfx:perf01:subject','Original subject 7 missing/failed');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original unchanged 64x128 input required');
end
settings=quasinewton_optim_config();
if settings.maxIter ~= 100 || ~settings.optIter || settings.nRandInit ~= 0
    error('hgfx:perf01:optimizer','Original optimizer options changed');
end
u=double(data.u(8,:))';
y=double(data.y(8,:))';
% Capturing output is outside any timing region; preserve original public API.
text=evalc(['fit=fitModel(y,u,' ...
    '''hgf_binary_config'',''unitsq_sgm_config'',' ...
    '''quasinewton_optim_config'');']);
if ~isfield(fit.optim,'iter') || ~isstruct(fit.optim.iter) || ...
   ~isfield(fit.optim.iter,'x') || ~isfield(fit.optim.iter,'val')
    error('hgfx:perf01:trace','Frozen public MATLAB optimizer history missing');
end
same_start=isequaln(fit.optim.init(:),double(old.optim.init(:))) && ...
    fit.c_opt.nRandInit==0;

% Export original inverse Hessian by public optimizer bookkeeping WITHOUT modifying source.
n_finite=sum(isfinite(fit.optim.iter.val));
if n_finite~=25 || size(fit.optim.iter.x,1)~=101 || ...
        size(fit.optim.iter.x,2)~=3 || ...
        numel(fit.optim.iter.invH)<23 || numel(fit.optim.iter.invH)>25
    error('hgfx:perf01:history','Unexpected original 101-slot or 25-finite Hessian history');
end
matrices=cell(1,numel(fit.optim.iter.invH));
for kk=1:numel(matrices)
    if ~isfield(fit.optim.iter.invH(kk),'T') || ...
            ~isequal(size(fit.optim.iter.invH(kk).T),[3,3])
        error('hgfx:perf01:Hessian','Missing original 3x3 inverse Hessian at slot %d',kk);
    end
    matrices{kk}=double(fit.optim.iter.invH(kk).T);
end
r=struct();
r.u=u;
r.y=y;
r.ign=find(isnan(u))';
r.irr=find(isnan(u)|isnan(y))';
r.c_prc=hgf_binary_config();
r.c_obs=unitsq_sgm_config();
r.c_opt=quasinewton_optim_config();
full=[r.c_prc.priormus(:)',r.c_obs.priormus(:)'];
prior_variances=[r.c_prc.priorsas(:)',r.c_obs.priorsas(:)'];
prior_variances(isnan(prior_variances))=0;
indices=find(prior_variances);
if ~isequal(indices,[13,14,15]) || ~isequal(full(indices),fit.optim.init(indices))
    error('hgfx:perf01:free','Frozen free-coordinate mapping changed');
end
objective=@(z)objective_at_free(z,r,full,indices,numel(r.c_prc.priormus));
opts=struct('min_steps',10);
probe=cell(1,n_finite);
for kk=1:n_finite
    x0=double(fit.optim.iter.x(kk,:))';
    record=struct();
    record.record_index_zero_based=kk-1;
    record.free_parameters=x0';
    record.objective_recomputed=double(objective(x0));
    [g,e]=riddersgradient(objective,x0,opts);
    record.grad=double(g(:))';
    record.ridders_error=double(e(:))';
    probe{kk}=record;
end

out=struct();
out.schema='perf01-subject7-bfgs-state-matlab-v1';
out.status='UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED';
out.model='hgf_binary';
out.trials=128;
out.subject_index_zero_based=7;
out.source_run_id='41863441006';
out.frozen_hgfx_sha=hgfx;
out.frozen_matlab_sha=ref;
out.source_input_sha256=src.hgfx_input_sha256;
out.source_config_sha256=src.hgfx_config_sha256;
out.original_raw_fits_verified=true;
out.frozen_start_matches=same_start;
out.n_rand_init=double(fit.c_opt.nRandInit);
out.fit_neg_lj=double(fit.optim.negLj);
out.original_final_full=old.optim.final;
out.final_full=fit.optim.final;
out.iter_x=fit.optim.iter.x;
out.iter_val=fit.optim.iter.val;
out.iter_inverse_hessian=[matrices]; % MATLAB JSON cell array retains each 3x3 matrix
out.iter_resets_one_based=double(fit.optim.iter.rst);
out.ridders_recomputed_history=[probe{:}];
out.ridders_min_steps=10;
out.finite_slots=n_finite;
out.fitModel_function_path=which('fitModel');
out.quasinewton_function_path=which('quasinewton_optim');
out.console_characters=numel(text);
out.note='Frozen public MATLAB fitModel plus original BFGS matrices and Ridders at all history records; no timers, no termination reason supplied.';
[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Cannot open source trace output');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
fprintf('Archived fresh public MATLAB trace; allocated slots=%d, finite values=%d, not number of executed iterations.\n', ...
    numel(fit.optim.iter.val),sum(isfinite(fit.optim.iter.val)));
end

function value=objective_at_free(free,r,initial,idx,nprc)
full=initial;
full(idx)=free(:)';
prc=full(1:nprc);
obs=full(nprc+1:end);
try
    [~,states]=hgf_binary(r,prc,'trans');
    logps=unitsq_sgm(r,states,obs);
    logps(r.irr)=[];
    logll=sum(logps);
    if isnan(logll)
        value=realmax;
        return
    end
    pidx=r.c_prc.priorsas;
    pidx(isnan(pidx))=0;
    pidx=find(pidx);
    oidx=r.c_obs.priorsas;
    oidx(isnan(oidx))=0;
    oidx=find(oidx);
    lp=sum(-0.5.*log(8*atan(1).*r.c_prc.priorsas(pidx)) - ...
        0.5.*(prc(pidx)-r.c_prc.priormus(pidx)).^2./r.c_prc.priorsas(pidx));
    lo=sum(-0.5.*log(8*atan(1).*r.c_obs.priorsas(oidx)) - ...
        0.5.*(obs(oidx)-r.c_obs.priormus(oidx)).^2./r.c_obs.priorsas(oidx));
    value=-(logll+lp+lo);
    if ~isfinite(value)
        value=realmax;
    end
catch
    value=realmax;
end
end
