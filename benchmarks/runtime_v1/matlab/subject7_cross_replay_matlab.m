function subject7_cross_replay_matlab(root,toolbox_root,fitted_root,output_path)
% Replay the exact two original optimizer endpoints from run 41863441006.
% No optimization, timing, new starts, modified inputs or new thresholds.
addpath(genpath(toolbox_root));

expected_hgfx='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
expected_matlab='2437f4dc241541072722a2695ddeca7b44d83dd3';
summary=jsondecode(fileread(fullfile(fitted_root,'summary-41863441006.json')));
if ~strcmp(summary.hgfx_sha,expected_hgfx) || ~strcmp(summary.matlab_sha,expected_matlab)
    error('hgfx:perf01:identity','Archived fitting report source identity changed');
end
hgfx=jsondecode(fileread(fullfile(fitted_root,'hgfx_raw.json')));
matlab=jsondecode(fileread(fullfile(fitted_root,'matlab_raw.json')));
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Unexpected frozen canonical dataset dimensions');
end
r=struct();
r.u=double(data.u(8,:))';
r.y=double(data.y(8,:))';
r.ign=[];
r.irr=[];
r.c_prc=hgf_binary_config;
r.c_obs=unitsq_sgm_config;
nprc=numel(r.c_prc.priormus);

source_labels={'hgfx','matlab'};
source_records={hgfx.cases(8),matlab.cases(8)};
cases=cell(1,2);
for k=1:2
    source=source_records{k};
    if source.subject_index_zero_based ~= 7 || ...
       ~source.start_matches_frozen_snapshot || source.n_rand_init ~= 0
        error('hgfx:perf01:source','Subject 7 source start/policy not verified');
    end
    full=double(source.optim.final(:))';
    rec=struct();
    rec.endpoint_source=source_labels{k};
    rec.transformed_final_vector=full;
    rec.status='NOT_RUN';
    rec.error_identifier='';
    rec.error_message='';
    rec.inf_states=[];
    rec.traj=struct();
    rec.trial_log_likelihoods=[];
    rec.yhat=[];
    rec.residuals=[];
    try
        if numel(full)~=numel(r.c_prc.priormus)+numel(r.c_obs.priormus)
            error('hgfx:perf01:vector','Unexpected parameter vector length');
        end
        [traj,inf_states]=hgf_binary(r,full(1:nprc),'trans');
        [logps,yhat,res]=unitsq_sgm(r,inf_states,full(nprc+1:end));
        rec.status='MATLAB_REPLAY_COMPLETED';
        rec.inf_states=inf_states;
        rec.traj=traj;
        rec.trial_log_likelihoods=logps(:);
        rec.yhat=yhat(:);
        rec.residuals=res(:);
    catch ME
        rec.status='MATLAB_REPLAY_ERROR';
        rec.error_identifier=ME.identifier;
        rec.error_message=ME.message;
    end
    cases{k}=rec;
end

out=struct();
out.schema='perf01-subject7-matlab-cross-replay-v1';
out.protocol='hgfx-matlab-runtime-1';
out.status='DIAGNOSTIC_UNFROZEN_NOT_TIMED';
out.product_sha=expected_hgfx;
out.oracle_sha=expected_matlab;
out.subject_index_zero_based=7;
out.trials=128;
out.source_run_id='41863441006';
out.matlab_release=version('-release');
out.resolved_hgf_binary=which('hgf_binary');
out.cases=[cases{:}];

[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Cannot write MATLAB replay report.');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
fprintf('PERF-01 subject 7 same-vector cross-replay recorded, no fitting or timing.\n');
end
