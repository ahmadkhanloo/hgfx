function subject7_omega_counterfactual_matlab(root,toolbox_root,original,output_path)
% PERF-01D original exact HGF 2x2 omega2/omega3 corner experiment.
% Author-side only; original MATLAB reference and full fit untouched.
addpath(genpath(toolbox_root));
[outdir,~,~]=fileparts(output_path);
if ~isfolder(outdir);mkdir(outdir);end

% Existing immutable three-vector experiment verifies original raw 64 SHA,
% original starts/subject/release and forwards each source's own endpoint.
baseline_file=fullfile(outdir,'matlab_original_three_baseline.json');
subject7_crossed_forward_matlab(root,toolbox_root,original,baseline_file);
baseline=jsondecode(fileread(baseline_file));
if ~strcmp(baseline.status, ...
        'SAME_VECTOR_FORWARD_DIAGNOSTIC_NO_FULL_FIT_NO_TIMING_NO_SCIENTIFIC_PASS') || ...
        numel(baseline.cases)~=3 || ...
        ~strcmp(baseline.cases(1).origin,'original_hgfx_fitted_endpoint') || ...
        ~strcmp(baseline.cases(2).origin,'original_matlab_fitted_endpoint')
    error('hgfx:perf01:source','Original three identical-vector reference not confirmed');
end
h=double(baseline.cases(1).full_transformed_vector(:))';
m=double(baseline.cases(2).full_transformed_vector(:))';
if numel(h)~=15 || numel(m)~=15 || ~isequal(isnan(h),isnan(m)) || ...
        ~isequaln(h(1:12),m(1:12)) || ...
        any(~isfinite([h(13),h(14),m(13),m(14)]))
    error('hgfx:perf01:vectors','Frozen fitted perceptual vectors changed');
end

% Predeclared 2^2 grid: original MATLAB (M/M), mixed H/M and M/H,
% and original HGFX (H/H). The observation logze parameter, full index 15,
% is not consumed by HGF forward. Mixed corners retain original MATLAB logze.
labels={'MM_original_matlab','HM_hgfx_omega2_matlab_omega3', ...
        'MH_matlab_omega2_hgfx_omega3','HH_original_hgfx'};
vHM=m; vHM(13)=h(13);
vMH=m; vMH(14)=h(14);
params={m,vHM,vMH,h};
omega2={'MATLAB','HGFX','MATLAB','HGFX'};
omega3={'MATLAB','MATLAB','HGFX','HGFX'};

data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original 64 by 128 inputs required');
end
r=struct();
r.u=double(data.u(8,:))';
r.y=double(data.y(8,:))';
r.ign=find(isnan(r.u))';
r.irr=find(isnan(r.u)|isnan(r.y))';
r.c_prc=hgf_binary_config();
r.c_obs=unitsq_sgm_config();
nprc=numel(r.c_prc.priormus);
if nprc~=14 || numel(r.c_obs.priormus)~=1
    error('hgfx:perf01:config','Original HGF 14+1 vector split changed');
end
rows=cell(1,4);
for j=1:4
    v=double(params{j});
    if ~isequal(isnan(v),isnan(h)) || numel(v)~=15
        error('hgfx:perf01:source','Original HGF 15-vector NaN mask changed');
    end
    if j==1
        traj=baseline.cases(2).traj;
        states=baseline.cases(2).inf_states;
    elseif j==4
        traj=baseline.cases(1).traj;
        states=baseline.cases(1).inf_states;
    else
        [traj,states]=hgf_binary(r,v(1:nprc),'trans');
    end
    if ~isequal(size(traj.mu),[128,3]) || ...
            ~isequal(size(traj.muhat),[128,3]) || ...
            ~isequal(size(traj.w),[128,2]) || ...
            ~isequal(size(states),[128,3,4])
        error('hgfx:perf01:shape','Original model 128-trial shape changed');
    end
    row=struct();
    row.corner=labels{j};
    row.omega2_from=omega2{j};
    row.omega3_from=omega3{j};
    row.status='EVALUATED_FROZEN_UNTIMED_MATLAB_FORWARD';
    row.full_transformed_vector=v;
    row.traj=traj;
    row.inf_states=states;
    rows{j}=row;
end
out=struct();
out.schema='perf01d-subject7-omega-counterfactual-matlab-v1';
out.status='AUTHOR_SIDE_2X2_OMEGA_FORWARD_DIAGNOSTIC_NO_FITTING_OR_SCIENTIFIC_PASS';
out.original_64_fit_run='41863441006';
out.frozen_hgfx_sha='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
out.frozen_matlab_sha='2437f4dc241541072722a2695ddeca7b44d83dd3';
out.original_raw_sha256=baseline.original_raw_sha256;
out.source_input_sha256=baseline.source_input_sha256;
out.source_config_sha256=baseline.source_config_sha256;
out.subject_index_zero_based=7;
out.trials=128;
out.model='hgf_binary';
out.observation='unitsq_sgm';
out.perceptual_free_coordinates_zero_based=[12,13];
out.observation_free_coordinate_zero_based=14;
out.observation_coordinate_role= ...
    'fixed_original_MATLAB_in_mixed_corners_not_used_in_perceptual_forward';
out.original_full_parameter_ends_preserved=true;
out.predeclared_corner_order=labels;
out.function_path=which('hgf_binary');
out.matlab_release=version('-release');
out.cases=[rows{:}];
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Cannot write original four fixed-vector HGF forward results');end
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
fprintf('PERF-01D original 2x2 mixed omega forward: all four corners, no optimizer or timer\n');
end
