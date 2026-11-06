function subject7_crossed_forward_matlab(root,toolbox_root,original,output_path)
% Source-locked original hgf_binary 8.2.0 same-vector forward controls.
% No optimizer is executed. No timing or scientific gate is issued.
addpath(genpath(toolbox_root));
hgfx='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
reference='2437f4dc241541072722a2695ddeca7b44d83dd3';
summary=jsondecode(fileread(fullfile(original,'summary-41863441006.json')));
if ~strcmp(summary.hgfx_sha,hgfx) || ~strcmp(summary.matlab_sha,reference) || ...
        ~strcmp(summary.github_run_id,'41863441006')
    error('hgfx:perf01:identity','Original 64-public-fit scientific SHA mismatch');
end
expected_h='6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb';
expected_m='2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98';
entries=summary.raw_evidence_sha256;
if isfield(entries,'hgfx_raw_json')
    hhash=entries.hgfx_raw_json;
    mhash=entries.matlab_raw_json;
else
    hhash=entries.('hgfx_raw.json');
    mhash=entries.('matlab_raw.json');
end
if ~strcmp(hhash,expected_h) || ~strcmp(mhash,expected_m)
    error('hgfx:perf01:archive','Frozen original raw checksums changed');
end
h=jsondecode(fileread(fullfile(original,'hgfx_raw.json')));
m=jsondecode(fileread(fullfile(original,'matlab_raw.json')));
if numel(h.cases)~=64 || numel(m.cases)~=64 || ...
        h.cases(8).subject_index_zero_based~=7 || ...
        m.cases(8).subject_index_zero_based~=7 || ...
        ~strcmp(h.cases(8).status,'HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION') || ...
        ~strcmp(m.cases(8).status,'MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION') || ...
        h.cases(8).n_rand_init~=0 || m.cases(8).n_rand_init~=0
    error('hgfx:perf01:subject','Original subject seven complete fitted evidence wrong');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original 64 by 128 binary dataset required');
end
cfg=jsondecode(fileread(fullfile(root,'configs','hgf_binary_128.json')));
r=struct();
r.u=double(data.u(8,:))';
r.y=double(data.y(8,:))';
r.ign=find(isnan(r.u))';
r.irr=find(isnan(r.u)|isnan(r.y))';
r.c_prc=hgf_binary_config();
r.c_obs=unitsq_sgm_config();
r.c_opt=quasinewton_optim_config();
nprc=numel(r.c_prc.priormus);
if nprc~=14 || numel(r.c_obs.priormus)~=1 || ...
        r.c_opt.nRandInit~=0 || r.c_opt.maxIter~=100
    error('hgfx:perf01:model','Original model parameter split or optimizer changed');
end
start=[r.c_prc.priormus(:)',r.c_obs.priormus(:)'];
snapshot=NaN(1,numel(cfg.transformed_start_full));
for i=1:numel(snapshot)
    item=cfg.transformed_start_full(i);
    if isfield(item,'decimal')
        snapshot(i)=str2double(item.decimal);
    elseif isfield(item,'special')
        snapshot(i)=str2double(item.special);
    else
        error('hgfx:perf01:snapshot','Unsupported frozen parameter representation');
    end
end
if ~isequaln(start,snapshot) || ...
        ~isequaln(start,double(h.cases(8).optim.init(:))') || ...
        ~isequaln(start,double(m.cases(8).optim.init(:))') || ...
        ~isequal(double(cfg.fit_free_indices_0based(:))',[12,13,14])
    error('hgfx:perf01:start','Original immutable start/free coordinate altered');
end
origins={'original_hgfx_fitted_endpoint', ...
         'original_matlab_fitted_endpoint','original_frozen_start'};
vectors={double(h.cases(8).optim.final(:))', ...
         double(m.cases(8).optim.final(:))',start};
rows=cell(1,3);
for k=1:numel(origins)
    param=vectors{k};
    if numel(param)~=15 || ~isequal(isnan(param),isnan(start))
        error('hgfx:perf01:params','Original 15-vector NaN mask changed');
    end
    [traj,states]=hgf_binary(r,param(1:nprc),'trans');
    if ~isequal(size(states),[128,3,4]) || ...
            ~isequal(size(traj.mu),[128,3]) || ...
            ~isequal(size(traj.muhat),[128,3])
        error('hgfx:perf01:shape','Frozen reference forward shape unexpected');
    end
    record=struct();
    record.origin=origins{k};
    record.status='EVALUATED_IDENTICAL_FROZEN_VECTOR_MATLAB';
    record.full_transformed_vector=param;
    record.traj=traj;
    record.inf_states=states;
    rows{k}=record;
end
result=struct();
result.schema='perf01d-subject7-crossed-forward-matlab-v1';
result.status='SAME_VECTOR_FORWARD_DIAGNOSTIC_NO_FULL_FIT_NO_TIMING_NO_SCIENTIFIC_PASS';
result.frozen_hgfx_sha=hgfx;
result.frozen_matlab_sha=reference;
result.source_run_id='41863441006';
result.original_raw_sha256=struct('hgfx_raw_json',expected_h,'matlab_raw_json',expected_m);
result.source_input_sha256=summary.hgfx_input_sha256;
result.source_config_sha256=summary.hgfx_config_sha256;
result.subject_index_zero_based=7;
result.trials=128;
result.model='hgf_binary';
result.perceptual_parameter_count=nprc;
result.observation_parameter_count=1;
result.free_indices_zero_based=[12,13,14];
result.anchor_origins=origins;
result.original_endpoints_unmodified=true;
result.function_path=which('hgf_binary');
result.matlab_release=version('-release');
result.cases=[rows{:}];
[d,~,~]=fileparts(output_path);
if ~isfolder(d); mkdir(d); end
fid=fopen(output_path,'w');
if fid<0; error('hgfx:perf01:output','Could not write reference forward');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(result));
fprintf('PERF01-D: evaluated %d identical archived full-forward MATLAB anchors, untimed; no science PASS\n',numel(result.cases));
end
