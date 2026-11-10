function run_compstat_rev24_panel_e_matlab(input_path, private_output)
% Frozen REV-2.4 Panel E original-endpoint objective evaluation (NO OPTIMIZER).
% Private trial-level sources and intermediate likelihoods must NEVER be
% published, uploaded as unrestricted artifacts, or checked into Git.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
toolbox = fullfile(root,'external','hgf-toolbox');
expected_ref = '2437f4dc241541072722a2695ddeca7b44d83dd3';
expected_release = '4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
[status, head] = system(sprintf('git -C "%s" rev-parse HEAD',toolbox));
assert(status==0 && strcmp(strtrim(head),expected_ref), ...
    'REV24E:referenceCommit', 'Wrong original frozen MATLAB HGF reference.');
addpath(genpath(toolbox));
doc = jsondecode(fileread(input_path));
assert(strcmp(char(doc.protocol),'compstat-rev2-4-objective-cross-eval-v1'));
assert(strcmp(char(doc.panel),'E') && doc.expected_cases==66);
assert(strcmp(char(doc.science_status),'NOT_EXECUTED'));
assert(numel(doc.cases)==66);
assert(~exist(private_output,'file'),'REV24E:overwrite', ...
    'Refuse to overwrite original Panel E result.');

out.protocol = char(doc.protocol);
out.panel = 'E';
out.source = 'matlab';
out.release_source_commit = expected_release;
out.matlab_reference_commit = expected_ref;
out.original_cohort_inputs_sha256 = char(doc.original_cohort_inputs_sha256);
out.matlab_version = version;
out.scientific_gate = 'NOT_ASSESSED_NO_HGFX_PAIR';
out.cases = cell(1,132);
idx = 0;
for k=1:66
    c = element(doc.cases,k);
    if k==1
        assert(strcmp(char(c.case_id),'D02_fit'));
        assert(strcmp(char(c.perceptual_model),'ehgf_binary') && ...
               strcmp(char(c.observation_model),'unitsq_sgm') && ...
               c.trials==320 && c.obs_prior_variance==0.5);
    elseif k==2
        assert(strcmp(char(c.case_id),'D08_fit'));
        assert(strcmp(char(c.perceptual_model),'uhgf') && ...
               strcmp(char(c.observation_model),'gaussian_obs') && ...
               c.trials==614 && c.obs_prior_variance==0.1);
    else
        assert(strcmp(char(c.case_id),sprintf('cohort64_subject_%02d',k-3)));
        assert(strcmp(char(c.perceptual_model),'hgf_binary') && ...
               strcmp(char(c.observation_model),'unitsq_sgm') && ...
               c.trials==128 && c.obs_prior_variance==1.0);
    end
    u = parse_vector(c.inputs);
    y = parse_vector(c.responses);
    assert(numel(u)==double(c.trials) && numel(y)==numel(u), ...
           'REV24E:trialCount', 'Original trial lengths differ.');
    [pc,oc] = resolve_original_configs(c,u);
    assert(numel(pc.priormus)+numel(oc.priormus)== ...
           (11 + 4*(k~=2)), 'REV24E:parameterCount', ...
           'Original transformed parameter dimensionality mismatch.');
    if isstruct(c.source_prior_variances)
        source = c.source_prior_variances;
        assert(isequaln(pc.priorsas(:)',parse_vector(source.perceptual)), ...
            'REV24E:perceptualConfig', 'Original perceptual prior mismatch.');
        assert(isequaln(oc.priorsas(:)',parse_vector(source.observation)), ...
            'REV24E:observationConfig', 'Original observation prior mismatch.');
    end
    for e=1:2
        idx=idx+1;
        if e==1
            side='matlab';
            vector=c.endpoints.matlab;
        else
            side='hgfx';
            vector=c.endpoints.hgfx;
        end
        out.cases{idx}=evaluate_one(c,side,vector,u,y,pc,oc);
    end
end
assert(idx==132);
folder=fileparts(private_output);
if ~isempty(folder) && ~exist(folder,'dir');mkdir(folder);end
fid=fopen(private_output,'w');assert(fid>=0);
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(out,'PrettyPrint',true));
fprintf('REV-2.4 PANEL E MATLAB: 132 slots retained, NO SCIENCE PASS.\n');
end

function [pc,oc]=resolve_original_configs(c,u)
pc=feval([char(c.perceptual_model) '_config']);
oc=feval([char(c.observation_model) '_config']);
if strcmp(char(c.case_id),'D02_fit')
    oc.logzesa=0.5;oc=align_priors(oc);
end
assert(numel(oc.priorsas)==1 && oc.priorsas==double(c.obs_prior_variance));
% Identical to frozen fitModel dataPrep placeholder substitutions.
n=min(20,numel(u));
v=var(u(1:n),1);
assert(v>0 && isfinite(v),'REV24E:inputVariance');
old=[99991,99992,99993,-99993,99994];
new=[u(1),v,log(v),-log(v),log(v)-2];
for j=1:numel(old)
    pc.priormus(pc.priormus==old(j))=new(j);
    pc.priorsas(pc.priorsas==old(j))=new(j);
end
end

function row=evaluate_one(c,side,vector,u,y,pc,oc)
row.case_id=char(c.case_id);
row.case_sha256=char(c.case_sha256);
row.at_original_endpoint=side;
row.source='matlab';
row.model=char(c.perceptual_model);
row.observation_model=char(c.observation_model);
row.valid=false;
row.rval=-1;
row.status='NOT_EXECUTED';
row.log_likelihood='NaN';
row.neg_log_likelihood='NaN';
row.neg_log_joint='NaN';
row.trial_log_likelihoods={};
row.perceptual_prior_total='NaN';
row.observation_prior_total='NaN';
row.error_type='';
row.error_message='';
row.first_causal_state='NOT_EXPORTED';
row.gradient='NOT_AVAILABLE';
if isempty(vector)
    row.status='INSUFFICIENT_REFERENCE_EVIDENCE';
    return
end
try
    theta=parse_vector(vector);
    nprc=numel(pc.priormus);
    priorsas=[pc.priorsas(:)',oc.priorsas(:)'];
    means=[pc.priormus(:)',oc.priormus(:)'];
    assert(numel(theta)==numel(means),'REV24E:thetaShape');
    free=find(~isnan(priorsas)&priorsas~=0);
    fixed=find(isnan(priorsas)|priorsas==0);
    assert(all(isfinite(theta(free))),'REV24E:nonFiniteFree');
    assert(isequaln(theta(fixed),means(fixed)),'REV24E:fixedDrift');
    r.u=u(:);r.y=y(:);
    r.ign=find(isnan(r.u))';
    r.irr=unique([r.ign,find(isnan(r.y))']);
    r.c_prc=pc;r.c_obs=oc;
    [~,states]=pc.prc_fun(r,theta(1:nprc),'trans');
    ll=oc.obs_fun(r,states,theta(nprc+1:end));
    ll=double(ll(:)');
    regular=ll;regular(r.irr)=[];
    logLl=sum(regular);
    if isnan(logLl); negLl=realmax;else;negLl=-logLl;end
    prc_idx=find(~isnan(pc.priorsas)&pc.priorsas~=0);
    obs_idx=find(~isnan(oc.priorsas)&oc.priorsas~=0);
    pprc=theta(1:nprc);
    pobs=theta(nprc+1:end);
    prc_terms=-0.5.*log(8*atan(1).*pc.priorsas(prc_idx)) ...
       -0.5.*(pprc(prc_idx)-pc.priormus(prc_idx)).^2./pc.priorsas(prc_idx);
    obs_terms=-0.5.*log(8*atan(1).*oc.priorsas(obs_idx)) ...
       -0.5.*(pobs(obs_idx)-oc.priormus(obs_idx)).^2./oc.priorsas(obs_idx);
    ptotal=sum(prc_terms);ototal=sum(obs_terms);
    negLj=-(logLl+ptotal+ototal);
    row.rval=0;
    row.log_likelihood=ieee(logLl);
    row.neg_log_likelihood=ieee(negLl);
    row.neg_log_joint=ieee(negLj);
    row.perceptual_prior_total=ieee(ptotal);
    row.observation_prior_total=ieee(ototal);
    row.trial_log_likelihoods=arrayfun(@ieee,ll,'UniformOutput',false);
    row.valid=numel(ll)==numel(u)&&all(isfinite(ll))&&...
           isfinite(logLl)&&isfinite(negLl)&&isfinite(negLj);
    if row.valid;row.status='VALID';else;row.status='INVALID_OBJECTIVE';end
catch ME
    row.error_type=ME.identifier;
    row.error_message=ME.message;
    row.status='EVALUATION_ERROR';
end
end

function v=parse_vector(x)
if isstruct(x)
    assert(isfield(x,'data')&&isfield(x,'shape'),'REV24E:sourceVectorShape');
    assert(prod(double(x.shape))==numel(x.data),'REV24E:archivedVectorLength');
    x=x.data;
end
if iscell(x)
    v=zeros(1,numel(x));
    for k=1:numel(x);v(k)=to_float(x{k});end
elseif isnumeric(x)
    v=double(x(:)');
elseif isstring(x)
    v=arrayfun(@to_float,x(:)');
elseif ischar(x)
    v=to_float(x);
else
    error('REV24E:unsupportedVectorEncoding');
end
end

function d=to_float(x)
if isempty(x)
    d=NaN;
elseif isnumeric(x) && isscalar(x)
    d=double(x);
elseif ischar(x)||isstring(x)
    switch char(x)
      case 'NaN'; d=NaN;
      case '+Inf'; d=Inf;
      case '-Inf'; d=-Inf;
      otherwise;error('REV24E:unexpectedString');
    end
else
    error('REV24E:unexpectedScalar');
end
end

function val=ieee(x)
if isnan(x);val='NaN';
elseif isinf(x)&&x>0;val='+Inf';
elseif isinf(x);val='-Inf';
else;val=double(x);end
end

function x=element(v,k)
if iscell(v);x=v{k};else;x=v(k);end
end
