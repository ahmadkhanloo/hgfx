function subject7_matlab_reference_sensitivity(root,toolbox_root,fitted_root,output_path)
% PERF-01D reference-only +/−eps(start) numerical-basin diagnostic.
% Scientific sources and original dataset/priors are unmodified. A newly
% composed objective MUST first reproduce the frozen fitModel endpoint.
addpath(genpath(toolbox_root));
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
r0=jsondecode(fileread(fullfile(fitted_root,'summary-41863441006.json')));
if ~strcmp(r0.matlab_sha,ref)
    error('hgfx:perf01:source','Original MATLAB evidence identity mismatch');
end
orig=jsondecode(fileread(fullfile(fitted_root,'matlab_raw.json')));
source=orig.cases(8);
if source.subject_index_zero_based~=7 || ...
    ~strcmp(source.status,'MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION')
    error('hgfx:perf01:source','Expected originally fitted subject 7.');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:dimensions','Wrong original dataset');
end
r=struct();
r.u=double(data.u(8,:))';
r.y=double(data.y(8,:))';
r.irr=[];
r.ign=[];
r.c_prc=hgf_binary_config();
r.c_obs=unitsq_sgm_config();
r.c_opt=quasinewton_optim_config();
init=[r.c_prc.priormus(:)',r.c_obs.priormus(:)'];
source_init=double(source.optim.init(:))';
source_final=double(source.optim.final(:))';
if ~isequaln(init,source_init) || r.c_opt.nRandInit~=0 || r.c_opt.maxIter~=100
    error('hgfx:perf01:start','Original frozen priors/optimization start differs');
end
sas=[r.c_prc.priorsas(:)',r.c_obs.priorsas(:)'];
sas(isnan(sas))=0;
opt_idx=find(sas);
n_prc=numel(r.c_prc.priormus);
f=@(x) obj_free(x,r,init,opt_idx,n_prc);
initial_free=init(opt_idx)';

out=struct();
out.schema='perf01-subject7-matlab-self-sensitivity-v1';
out.status='DIAGNOSTIC_ONLY_NOT_SCIENTIFIC_PASS_NOT_TIMED';
out.source_run_id='41863441006';
out.model='hgf_binary';
out.trials=128;
out.subject_index_zero_based=7;
out.matlab_reference_sha=ref;
out.matlab_release=version('-release');
out.reference_function_paths=struct( ...
    'hgf_binary',which('hgf_binary'), ...
    'unitsq_sgm',which('unitsq_sgm'), ...
    'quasinewton_optim',which('quasinewton_optim'));
out.perturbation='Each optimized initial coordinate once by +/-eps(x), preserving original prior distribution and frozen objective.';
out.original_full_final=source_final;
out.opt_idx_one_based=opt_idx;
out.original_optimal_negative_log_joint=double(source.optim.negLj);
out.reproduction=struct();
out.perturbations=struct('free_coord_zero_based',{}, ...
    'original_start',{},'step_size',{},'signed_step',{}, ...
    'status',{},'optimized_full_final',{},'negative_log_joint',{}, ...
    'max_endpoint_shift',{},'outside_old_v1_final_parameter_tolerance',{}, ...
    'error_identifier',{},'error_message',{});

% The independently composed exact-form reference objective MUST reproduce
% fitModel's unperturbed optimization to existing frozen M10 tolerance.
baseline=run_once(f,initial_free,init,opt_idx,r.c_opt,source_final,source.optim.negLj);
out.reproduction=baseline;
if ~strcmp(baseline.status,'COMPLETED') || ...
    baseline.outside_old_v1_final_parameter_tolerance || ...
    abs(baseline.negative_log_joint-double(source.optim.negLj)) > ...
        (3e-10 + 3e-8*abs(double(source.optim.negLj)))
    out.classification='BASELINE_SOURCE_OBJECTIVE_REPLICA_NOT_VERIFIED';
else
    for i=1:numel(initial_free)
        origin=initial_free(i);
        step=eps(origin);
        for signnum=[-1,1]
            start=initial_free;
            start(i)=start(i)+signnum*step;
            probe=run_once(f,start,init,opt_idx,r.c_opt,source_final,source.optim.negLj);
            item=struct();
            item.free_coord_zero_based=i-1;
            item.original_start=origin;
            item.step_size=step;
            item.signed_step=signnum*step;
            item.status=probe.status;
            item.optimized_full_final=probe.optimized_full_final;
            item.negative_log_joint=probe.negative_log_joint;
            item.max_endpoint_shift=probe.max_endpoint_shift;
            item.outside_old_v1_final_parameter_tolerance= ...
                probe.outside_old_v1_final_parameter_tolerance;
            item.error_identifier=probe.error_identifier;
            item.error_message=probe.error_message;
            out.perturbations(end+1)=item; %#ok<AGROW>
        end
    end
    any_sensitivity=any([out.perturbations.outside_old_v1_final_parameter_tolerance]);
    if any_sensitivity
        out.classification='REFERENCE_SELF_SENSITIVITY_CANDIDATE_NOT_INDEPENDENTLY_REVIEWED';
    else
        out.classification='NO_REFERENCE_SELF_SENSITIVITY_BEYOND_M10_GATE_DEMONSTRATED';
    end
end
[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Cannot open reference sensitivity evidence');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
fprintf('MATLAB reference-only optimizer sensitivity report: %s\n',out.classification);
if strcmp(out.classification,'BASELINE_SOURCE_OBJECTIVE_REPLICA_NOT_VERIFIED')
    error('hgfx:perf01:replica','Reference standalone objective failed to reproduce official fit; report preserved');
end
end

function report=run_once(fun,free_start,template,opt_idx,settings,reference_final,source_joint)
report=struct();
report.status='NOT_RUN';
report.optimized_full_final=[];
report.negative_log_joint=[];
report.max_endpoint_shift=[];
report.outside_old_v1_final_parameter_tolerance=true;
report.error_identifier='';
report.error_message='';
try
    if ~isfinite(fun(free_start))
        error('hgfx:perf01:objective','Nonfinite start at frozen original objective');
    end
    optim=quasinewton_optim(fun,free_start,settings);
    full=template;
    full(opt_idx)=optim.argMin(:)';
    reference=double(reference_final(:))';
    if ~isequal(size(reference),size(full))
        error('hgfx:perf01:shape','Unexpected full fitted-vector shape');
    end
    matched_nan=isequal(isnan(full),isnan(reference));
    matched_posinf=isequal(isinf(full)&full>0,isinf(reference)&reference>0);
    matched_neginf=isequal(isinf(full)&full<0,isinf(reference)&reference<0);
    finite=isfinite(full)&isfinite(reference);
    if any(finite)
        report.max_endpoint_shift=max(abs(full(finite)-reference(finite)));
    end
    ok=matched_nan && matched_posinf && matched_neginf && ...
        all(abs(full(finite)-reference(finite)) <= ...
            3e-10+3e-8*abs(reference(finite)));
    report.status='COMPLETED';
    report.optimized_full_final=full;
    report.negative_log_joint=double(optim.valMin);
    report.outside_old_v1_final_parameter_tolerance=~ok;
catch ME
    report.status='ERROR';
    report.error_identifier=ME.identifier;
    report.error_message=ME.message;
end
end

function value=obj_free(free,r,template,idx,nprc)
full=template;
full(idx)=free(:)';
pprc=full(1:nprc);
pobs=full(nprc+1:end);
try
    [~,states]=hgf_binary(r,pprc,'trans');
    logps=unitsq_sgm(r,states,pobs);
    logps(r.irr)=[];
    logll=sum(logps);
    if isnan(logll)
        value=realmax;
        return;
    end
    prc_idx=r.c_prc.priorsas;
    prc_idx(isnan(prc_idx))=0;
    prc_idx=find(prc_idx);
    obs_idx=r.c_obs.priorsas;
    obs_idx(isnan(obs_idx))=0;
    obs_idx=find(obs_idx);
    logprc=sum(-0.5.*log(8*atan(1).*r.c_prc.priorsas(prc_idx)) - ...
        0.5.*(pprc(prc_idx)-r.c_prc.priormus(prc_idx)).^2./r.c_prc.priorsas(prc_idx));
    logobs=sum(-0.5.*log(8*atan(1).*r.c_obs.priorsas(obs_idx)) - ...
        0.5.*(pobs(obs_idx)-r.c_obs.priormus(obs_idx)).^2./r.c_obs.priorsas(obs_idx));
    value=-(logll+logprc+logobs);
    if ~isfinite(value)
        value=realmax;
    end
catch
    value=realmax;
end
end
