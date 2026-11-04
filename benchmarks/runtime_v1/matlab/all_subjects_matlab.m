function all_subjects_matlab(root,toolbox_root,output_path)
% PERF-01B/D fixed-vector 64-subject cohort audit, MATLAB HGF 8.2.0.
% This script does NOT time any call and does NOT fit any parameters.
addpath(genpath(toolbox_root));
manifest=jsondecode(fileread(fullfile(root,'inputs_manifest.json')));
cfg_manifest=jsondecode(fileread(fullfile(root,'resolved_configs_manifest.json')));
if ~strcmp(manifest.matlab_oracle_sha,'2437f4dc241541072722a2695ddeca7b44d83dd3') || ...
        ~strcmp(cfg_manifest.matlab_reference_expected_sha, ...
                '2437f4dc241541072722a2695ddeca7b44d83dd3')
    error('hgfx:perf01:oracle','Unexpected reference SHA.');
end
models={'hgf_binary','ehgf_binary','uhgf_binary'};
horizons=[128,512,1024];
result=struct();
result.schema='perf01-all-subject-matlab-v1';
result.protocol_id='hgfx-matlab-runtime-1';
result.status='DIAGNOSTIC_ONLY_NO_TIMING_NO_FITTING';
result.oracle_sha='2437f4dc241541072722a2695ddeca7b44d83dd3';
result.matlab_release=version('-release');
result.matlab_version=version;
result.function_paths=struct();
for mi=1:numel(models)
    result.function_paths.(models{mi})=which(models{mi});
end
result.function_paths.unitsq_sgm=which('unitsq_sgm');
result.function_paths.fitModel=which('fitModel');
rows=cell(1,numel(models)*numel(horizons)*64);
ri=0;
for ni=1:numel(horizons)
    n=horizons(ni);
    data=jsondecode(fileread(fullfile(root,'inputs',sprintf('binary_%d_s64.json',n))));
    if ~isequal(size(data.u),[64,n]) || ~isequal(size(data.y),[64,n])
        error('hgfx:perf01:dimensions','Unexpected dimensions in canonical data.');
    end
    for mi=1:numel(models)
        model=models{mi};
        snap=jsondecode(fileread(fullfile(root,'configs', ...
            sprintf('%s_%d.json',model,n))));
        theta=decode_records(snap.transformed_start_full);
        r=struct();
        r.c_prc=feval([model '_config']);
        r.c_obs=unitsq_sgm_config();
        n_prc=numel(r.c_prc.priormus);
        n_obs=numel(r.c_obs.priormus);
        ref_means=decode_param_vector(snap.perceptual.parameters,'prior_mean');
        ref_vars=decode_param_vector(snap.perceptual.parameters,'prior_variance');
        ref_obs_means=decode_param_vector(snap.observation.parameters,'prior_mean');
        ref_obs_vars=decode_param_vector(snap.observation.parameters,'prior_variance');
        config_ok=numel(theta)==n_prc+n_obs && ...
            isequaln(r.c_prc.priormus(:)',theta(1:n_prc)) && ...
            isequaln(r.c_obs.priormus(:)',theta(n_prc+1:end)) && ...
            isequaln(r.c_prc.priormus(:)',ref_means) && ...
            isequaln(r.c_prc.priorsas(:)',ref_vars) && ...
            isequaln(r.c_obs.priormus(:)',ref_obs_means) && ...
            isequaln(r.c_obs.priorsas(:)',ref_obs_vars);
        for subject_idx=1:64
            row=struct();
            row.model=model;
            row.trials=n;
            row.subject_index_zero_based=subject_idx-1;
            row.config_matches_snapshot=config_ok;
            row.forward_status='NOT_RUN';
            row.objective_status='NOT_RUN';
            row.negative_log_joint=[];
            row.negative_log_likelihood=[];
            row.valid_likelihood_trials=[];
            row.error_identifier='';
            row.error_message='';
            if ~config_ok
                row.forward_status='BLOCKED_CONFIG_MISMATCH';
                row.objective_status='BLOCKED_CONFIG_MISMATCH';
            else
                r.u=double(data.u(subject_idx,:))';
                r.y=double(data.y(subject_idx,:))';
                r.ign=find(isnan(r.u))';
                r.irr=union(find(isnan(r.u)),find(isnan(r.y)))';
                try
                    [~,states]=feval(model,r,theta(1:n_prc),'trans');
                    if size(states,1)~=n || size(states,2)~=3 || size(states,3)~=4
                        row.forward_status='INVALID_SHAPE';
                        row.objective_status='INVALID_SHAPE';
                    else
                        row.forward_status='COMPLETE';
                        try
                            logps=unitsq_sgm(r,states,theta(n_prc+1:end));
                            regular=true(n,1);
                            regular(r.irr)=false;
                            logll=sum(logps(regular));
                            joint=-(logll+gaussian_prior(theta(1:n_prc),r.c_prc.priormus, ...
                                r.c_prc.priorsas)+gaussian_prior(theta(n_prc+1:end), ...
                                r.c_obs.priormus,r.c_obs.priorsas));
                            if ~isfinite(joint)
                                row.objective_status='INVALID_OR_ERROR';
                            else
                                row.objective_status='COMPLETE';
                                row.negative_log_joint=joint;
                                row.negative_log_likelihood=-logll;
                                row.valid_likelihood_trials=sum(regular);
                            end
                        catch ME2
                            row.objective_status='INVALID_OR_ERROR';
                            row.error_identifier=ME2.identifier;
                            row.error_message=ME2.message;
                        end
                    end
                catch ME
                    row.forward_status='INVALID_OR_ERROR';
                    row.objective_status='INVALID_OR_ERROR';
                    row.error_identifier=ME.identifier;
                    row.error_message=ME.message;
                end
            end
            ri=ri+1;
            rows{ri}=row;
        end
    end
end
if ri~=576
    error('hgfx:perf01:registry','Expected 576 model-subject rows.');
end
result.cases=[rows{:}];
[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Could not write cohort report.');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(result));
fprintf('PERF-01 576-row MATLAB fixed-vector cohort audit saved (not timed).\n');
end

function a=decode_records(items)
a=zeros(1,numel(items));
for k=1:numel(items)
    if iscell(items);v=items{k};else;v=items(k);end
    if isfield(v,'decimal');a(k)=str2double(v.decimal);
    elseif isfield(v,'special');a(k)=str2double(v.special);
    else;error('hgfx:perf01:decode','Missing float metadata.');end
end
end

function a=decode_param_vector(items,field)
a=zeros(1,numel(items));
for k=1:numel(items)
    if iscell(items);v=items{k};else;v=items(k);end
    a(k)=decode_records(v.(field));
end
end

function v=gaussian_prior(p,mus,sas)
sas(isnan(sas))=0;
idx=find(sas);
v=sum(-0.5*log(2*pi*sas(idx))-0.5*((p(idx)-mus(idx)).^2)./sas(idx));
end
