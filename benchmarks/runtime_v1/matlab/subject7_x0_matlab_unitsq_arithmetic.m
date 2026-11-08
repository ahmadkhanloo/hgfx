function subject7_x0_matlab_unitsq_arithmetic(root, toolbox_root, python_stage_file, source_h_file, source_m_file, output_file)
% Source-algebra intermediate diagnostics only: exact original unitsq_sgm
% MATLAB source formula evaluated at BOTH authentic source predictors for
% ALL 71 original Ridders x nodes and all 128 original trials.
% Frozen native MATLAB observation/fitModel are never edited. Preserve
% any mismatched source native or formula bits in raw output for review.
addpath(genpath(toolbox_root));
hgfx_sha='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
matlab_sha='2437f4dc241541072722a2695ddeca7b44d83dd3';
root_prefix=[strrep(toolbox_root,'\','/'),'/'];
files={which('fitModel'),which('hgf_binary'),which('unitsq_sgm')};
for i=1:numel(files)
    if isempty(files{i}) || ~startsWith(strrep(files{i},'\','/'),root_prefix)
        error('hgfx:perf01:lineage','Original frozen MATLAB model source is unavailable');
    end
end
p=jsondecode(fileread(python_stage_file));
h=jsondecode(fileread(source_h_file));
m=jsondecode(fileread(source_m_file));
if ~strcmp(p.schema,'perf01d-authentic-hgfx-unitsq-arithmetic-stages-71x128x2-v1') || ...
   ~strcmp(p.original_63_64_fit,'63/64 SCIENTIFIC NONPASS') || ...
   ~strcmp(h.original_scientific_fitting,'63/64 SCIENTIFIC NONPASS') || ...
   ~strcmp(m.original_scientific_fitting,'63/64 SCIENTIFIC NONPASS') || ...
   ~strcmp(p.frozen_hgfx_sha,hgfx_sha) || ~strcmp(p.frozen_matlab_sha,matlab_sha) || ...
   ~strcmp(p.source_genuine_run,'42404444341') || ...
   ~strcmp(p.source_genuine_sha,'a6168bb2b1be07a0f084abc07599e9ffda61b22b') || ...
   ~strcmp(p.independent_scientific_reviewer,'NOT_RECEIVED') || ...
   ~strcmp(p.perf01c,'NOT_FROZEN') || ...
   numel(p.nodes)~=71 || numel(h.nodes)~=71 || numel(m.nodes)~=71
    error('hgfx:perf01:original','Original failed 71-node source provenance changed');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.y),[64,128]) || ~isequal(size(data.u),[64,128])
    error('hgfx:perf01:cohort','Original subject7 failed scientific source changed');
end
y=double(data.y(8,:))';u=double(data.u(8,:))';
cfg=quasinewton_optim_config();
if cfg.nRandInit~=0 || cfg.maxIter~=100 || ~cfg.optIter || ...
   ~strcmp(func2str(cfg.opt_algo),'quasinewton_optim')
    error('hgfx:perf01:optim','Frozen original native optimizer config changed');
end
native=[];
native_console=evalc('native=fitModel(y,u,''hgf_binary_config'',''unitsq_sgm_config'',cfg);');
obs_fun=native.c_obs.obs_fun;
if ~strcmp(func2str(obs_fun),'unitsq_sgm') || native.c_obs.predorpost~=1 || ...
   ~startsWith(strrep(which(func2str(obs_fun)),'\','/'),root_prefix) || ...
   ~strcmp(func2str(native.c_prc.prc_fun),'hgf_binary')
    error('hgfx:perf01:obs','Native original observation family and source path changed');
end
all_prior_means=[native.c_prc.priormus,native.c_obs.priormus];
all_prior_var=[native.c_prc.priorsas,native.c_obs.priorsas];
all_prior_var(isnan(all_prior_var))=0;
free=find(all_prior_var);
if ~isequal(free(:)',[13,14,15]) || ...
   ~isequal(double(all_prior_means(free)),[-3,-6,3.871201010907891])
    error('hgfx:perf01:free','Original free coordinates/prior means changed');
end
prc_len=numel(native.c_prc.priormus);
obs_len=numel(native.c_obs.priormus);
fields={'x','y','zeta','one_minus_x','logx_raw','logx_alt',...
'logx_selected','log1mx_raw','log1mx_alt','log1mx_selected',...
'pow_one_minus_x','pow_x','normalizer_sum','log_normalizer',...
'log_ratio','response_times_ze','response_term','base_term',...
'positive_terms_sum','formula_logp'};
rows=cell(1,71);
native_failure_count=0;
formula_failure_count=0;
for i=1:71
    src=p.nodes(i);hh=h.nodes(i);mm=m.nodes(i);
    xx=double(src.x(:))';
    xhex=cellstr(num2hex(xx(:)));
    if src.original_node_index~=i-1 || hh.ordinal~=i-1 || mm.ordinal~=i-1 || ...
       ~isequal(xhex(:),cellstr(string(mm.x_hex(:)))) || ...
       ~isequal(xhex(:),cellstr(string(hh.x_hex(:)))) || ~all(isfinite(xx))
        error('hgfx:perf01:x','Original same-x source node location/order bits altered');
    end
    full=all_prior_means;
    full(free)=xx;
    obs=full(prc_len+1:prc_len+obs_len);
    ze=exp(obs(1));
    if ~strcmp(num2hex(ze),num2hex(double(hh.native_zeta))) || ...
       ~strcmp(num2hex(ze),num2hex(double(mm.native_zeta)))
        error('hgfx:perf01:zeta','Original native source zeta bits changed');
    end
    case_rows=cell(1,2);
    for c=1:2
        prior=src.cases(c);
        case_name=char(prior.input_case);
        if (c==1 && ~strcmp(case_name,'hgfx_predictor')) || ...
           (c==2 && ~strcmp(case_name,'matlab_predictor'))
            error('hgfx:perf01:case','Original predictor case order changed');
        end
        prediction=double(prior.input_prediction(:));
        if numel(prediction)~=128 || ~all(isfinite(prediction)) || ...
           any(prediction<=0) || any(prediction>=1)
            error('hgfx:perf01:predictor','Original native observation predictor missing/invalid');
        end
        if c==1
            source_pred=double(hh.native_prediction_level1(:));
            native_reference=double(mm.matlab_unitsq_on_hgfx_prediction_logp(:));
        else
            source_pred=double(mm.native_prediction_level1(:));
            native_reference=double(mm.native_logp(:));
        end
        if ~isequal(cellstr(num2hex(prediction)),cellstr(num2hex(source_pred)))
            error('hgfx:perf01:bits','Original source predictor bits do not match real original input');
        end
        % Native actual frozen public source observation function on exactly
        % the original predictor. Other infStates cells are never consumed
        % by predorpost=1, and are not modified upstream in either toolbox.
        inf=zeros(128,3,4);
        inf(:,1,1)=prediction;
        native_ll=obs_fun(native,inf,obs);
        native_ll=double(native_ll(:));
        if numel(native_ll)~=128 || ~all(isfinite(native_ll))
            error('hgfx:perf01:logp','Original native source did not return 128 finite trial likelihoods');
        end
        native_mismatches=find(~strcmp(cellstr(num2hex(native_ll)),...
                                       cellstr(num2hex(native_reference))))-1;
        native_failure_count=native_failure_count+numel(native_mismatches);
        % Direct transparent source algebra. This must reproduce native
        % untouched unitsq_sgm at exact binary64 bits for inference.
        one=1-prediction;
        logx_raw=log(prediction);
        logx_alt=log1p(prediction-1);
        logx=logx_raw;
        mask_one=1-prediction<1e-4;
        logx(mask_one)=logx_alt(mask_one);
        log1mx_raw=log(1-prediction);
        log1mx_alt=log1p(-prediction);
        log1mx=log1mx_raw;
        mask_two=prediction<1e-4;
        log1mx(mask_two)=log1mx_alt(mask_two);
        p1=(1-prediction).^ze;
        p2=prediction.^ze;
        normalizer=p1+p2;
        log_norm=log(normalizer);
        ratio=logx-log1mx;
        yze=y.*ze;
        response_term=yze.*ratio;
        base_term=ze.*log1mx;
        added=response_term+base_term;
        formula=added-log_norm;
        vals={prediction,y,repmat(ze,128,1),one,logx_raw,logx_alt,...
              logx,log1mx_raw,log1mx_alt,log1mx,p1,p2,normalizer,...
              log_norm,ratio,yze,response_term,base_term,added,formula};
        if ~all(cellfun(@(z)isequal(size(z),[128,1]) && all(isfinite(z)),vals))
            error('hgfx:perf01:formula','Original MATLAB staged formula produced missing/nonfinite values');
        end
        formula_mismatches=find(~strcmp(cellstr(num2hex(formula)),...
                                        cellstr(num2hex(native_ll))))-1;
        formula_failure_count=formula_failure_count+numel(formula_mismatches);
        stage=struct();
        for k=1:numel(fields)
            stage.(fields{k})=vals{k}';
        end
        record=struct();
        record.input_case=case_name;
        record.input_prediction=prediction';
        record.native_matlab_observation_ll=native_ll';
        record.old_genuine_matlab_observation_ll=native_reference';
        record.native_vs_old_source_differences=native_mismatches';
        record.formula_vs_new_native_differences=formula_mismatches';
        record.stage_arrays=stage;
        case_rows{c}=record;
    end
    entry=struct();
    entry.original_node_index=i-1;
    entry.x=xx;
    entry.cases=case_rows;
    rows{i}=entry;
end
out=struct();
out.schema='perf01d-authentic-matlab-unitsq-arithmetic-stages-71x128x2-v1';
out.status='AUTHOR_SIDE_SOURCE_STAGE_REPLAY_UNVERIFIED_UNTIL_INDEPENDENT_VERIFIER';
out.frozen_hgfx_sha=hgfx_sha;out.frozen_matlab_sha=matlab_sha;
out.source_genuine_run='42404444341';
out.source_genuine_sha='a6168bb2b1be07a0f084abc07599e9ffda61b22b';
out.original_63_64_fit='63/64 SCIENTIFIC NONPASS';
out.original_subject7_failures=struct('traj_mu',4,'traj_muhat',4);
out.node_count=71;out.trials=128;out.cases_each_node=2;
out.stage_fields=fields;
out.status_counts=struct('native_against_genuine_previous_matlab_mismatch_counts',native_failure_count,...
                         'formula_against_new_native_mismatch_counts',formula_failure_count);
out.native_fit_unmodified=true;
out.native_fit_console_length=numel(native_console);
out.native_obs_model=func2str(obs_fun);
out.native_obs_file=which(func2str(obs_fun));
out.native_fitmodel_file=which('fitModel');
out.nodes=rows;
out.matlab_version=version;out.matlab_release=version('-release');
out.github_run_id=getenv('GITHUB_RUN_ID');
out.tested_sha=getenv('GITHUB_SHA');
out.independent_scientific_reviewer='NOT_RECEIVED';
out.perf01c='NOT_FROZEN';out.timing='NOT_RUN';out.gpu='NOT_RUN';
[folder,~,~]=fileparts(output_file);
if ~isfolder(folder);mkdir(folder);end
fid=fopen(output_file,'w');
if fid<0;error('hgfx:perf01:save','Cannot archive full original MATLAB source intermediate arrays');end
clean=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
clear clean;
fprintf('Real frozen MATLAB original 71x2x128 source stage completed. Old native mismatches: %d. Formula mismatches: %d. SCIENCE 63/64 NONPASS\n',native_failure_count,formula_failure_count);
end
