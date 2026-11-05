function subject7_gradient_probes_matlab(root,toolbox_root,archive,output_path)
% Untimed frozen MATLAB Ridders gradient at exact archived public-fit anchors.
% Every original subject/parameter vector is preserved; no optimizer is run.
addpath(genpath(toolbox_root));
hgfx='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
summary=jsondecode(fileread(fullfile(archive,'summary.json')));
if ~strcmp(summary.github_run_id,'42115887599') || ...
        ~strcmp(summary.candidate_sha,'b378fef6ff93f6efa041f4e8304dafba742ae4ab') || ...
        ~strcmp(summary.frozen_hgfx_sha,hgfx) || ~strcmp(summary.frozen_matlab_sha,ref)
    error('hgfx:perf01:source','Archived original public-fit trace SHA mismatch');
end
expected_hgfx='6fe10be1dd1860612859e6efbe7bee13717e4787aed4a62f0e6b67a2072aac7a';
expected_matlab='ce4a96e6eb2aad48ee08c39f0361c0cebd5d2306b048b9674c96a45a4570a40f';
% MATLAB jsondecode may normalize JSON dotted keys to valid identifiers.
entry=summary.raw_evidence_sha256;
if isfield(entry,'hgfx_raw_json')
    sha_hgfx=entry.hgfx_raw_json;
    sha_matlab=entry.matlab_raw_json;
else
    sha_hgfx=entry.('hgfx_raw.json');
    sha_matlab=entry.('matlab_raw.json');
end
if ~strcmp(sha_hgfx,expected_hgfx) || ~strcmp(sha_matlab,expected_matlab)
    error('hgfx:perf01:hash','Original recorded raw trace hashes mismatch');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original input matrix must be 64x128');
end
r=struct();
r.u=double(data.u(8,:))';
r.y=double(data.y(8,:))';
r.irr=[];
r.ign=[];
r.c_prc=hgf_binary_config();
r.c_obs=unitsq_sgm_config();
r.c_opt=quasinewton_optim_config();
if r.c_opt.maxIter~=100 || r.c_opt.nRandInit~=0 || ~r.c_opt.optIter
    error('hgfx:perf01:optimizer','Frozen optimizer config unexpectedly changed');
end
initial=[r.c_prc.priormus(:)',r.c_obs.priormus(:)'];
prior_sas=[r.c_prc.priorsas(:)',r.c_obs.priorsas(:)'];
prior_sas(isnan(prior_sas))=0;
indices=find(prior_sas);
if ~isequal(indices,[13,14,15]) || ~isequal(initial(indices),[-3,-6,3.871201010907891])
    error('hgfx:perf01:start','Frozen initial parameters/free indices changed');
end
fun=@(x) objective_at_free(x,r,initial,indices,numel(r.c_prc.priormus));
anchor_indices=[0,1,13,14,23];
name={'hgfx','matlab'};
rows=cell(1,10);
k=0;
for n=1:2
    old=jsondecode(fileread(fullfile(archive,[name{n},'_raw.json'])));
    if old.subject_index_zero_based~=7 || old.trials~=128 || ...
            ~strcmp(old.frozen_hgfx_sha,hgfx) || ~strcmp(old.frozen_matlab_sha,ref) || ...
            ~strcmp(old.source_run_id,'41863441006') || ...
            ~old.frozen_start_matches || ~old.original_raw_fits_verified || old.n_rand_init~=0
        error('hgfx:perf01:archive','Original trace identity differs for %s',name{n});
    end
    if ~isequal(size(old.iter_x),[101,3]) || numel(old.iter_val)~=101
        error('hgfx:perf01:dimensions','Original preallocated trace shape wrong');
    end
    if ~isequal(old.iter_x(1,:),initial(indices))
        error('hgfx:perf01:identity','Original full-fit init not reproduced');
    end
    for ii=1:numel(anchor_indices)
        index=anchor_indices(ii);
        k=k+1;
        x=double(old.iter_x(index+1,:))';
        original_value=double(old.iter_val(index+1));
        if ~all(isfinite(x)) || ~isfinite(original_value)
            error('hgfx:perf01:anchor','Original anchor index %d not fully finite',index);
        end
        row=struct();
        row.anchor_origin=name{n};
        row.record_index_zero_based=index;
        row.free_parameters=x';
        row.archived_iter_val=original_value;
        row.status='NOT_EVALUATED';
        row.objective=[];
        row.ridders_gradient=[];
        row.ridders_error=[];
        row.archived_objective_abs_diff=[];
        row.error_identifier='';
        row.error_message='';
        try
            scalar=double(fun(x));
            opts=struct('min_steps',10);
            [grad,error]=riddersgradient(fun,x,opts);
            row.objective=scalar;
            row.ridders_gradient=double(grad(:))';
            row.ridders_error=double(error(:))';
            row.archived_objective_abs_diff=abs(scalar-original_value);
            row.status='EVALUATED';
        catch ME
            row.status='ERROR';
            row.error_identifier=ME.identifier;
            row.error_message=ME.message;
        end
        rows{k}=row;
    end
end
report=struct();
report.schema='perf01d-subject7-matlab-same-vector-gradient-v1';
report.status='AUTHOR_SIDE_DIAGNOSTIC_UNTIMED_NO_FIT_NO_GATE_PASS';
report.frozen_hgfx_sha=hgfx;
report.frozen_matlab_sha=ref;
report.original_trace_run='42115887599';
report.original_trace_sha='b378fef6ff93f6efa041f4e8304dafba742ae4ab';
% MATLAB struct field names cannot contain dots; comparator canonicalizes.
report.original_trace_raw_sha256=struct( ...
    'hgfx_raw_json',expected_hgfx,'matlab_raw_json',expected_matlab);
report.source_run_id='41863441006';
report.subject_index_zero_based=7;
report.trials=128;
report.model='hgf_binary';
report.observation='unitsq_sgm';
report.free_indices_zero_based=[12,13,14];
report.gradient_method='frozen_Ridders_min_steps_10';
report.anchor_indices_zero_based=anchor_indices;
report.function_paths=struct('hgf_binary',which('hgf_binary'), ...
    'unitsq_sgm',which('unitsq_sgm'), ...
    'riddersgradient',which('riddersgradient'), ...
    'riddersdiff',which('riddersdiff'));
report.cases=[rows{:}];
[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Could not create gradient diagnostic report');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(report));
fprintf('PERF-01D MATLAB anchor gradients: %d cases, all statuses stored, no timings\n',numel(report.cases));
if any(~strcmp({report.cases.status},'EVALUATED'))
    error('hgfx:perf01:gradient','Some original reference gradient probes failed; raw evidence retained');
end
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
