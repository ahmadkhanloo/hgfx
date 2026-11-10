function run_compstat_rev24_ehgf019_matlab(manifest_path, output_path)
% Prospectively frozen REV-2.4 D019 diagnostic: original MATLAB HGF 8.2.0.
% ONE original eHGF binary 128-trial vector; no optimization/fits/grid reruns.
root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
toolbox=fullfile(root,'external','hgf-toolbox');
reference='2437f4dc241541072722a2695ddeca7b44d83dd3';
release='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
[status,head]=system(sprintf('git -C "%s" rev-parse HEAD',toolbox));
assert(status==0 && strcmp(strtrim(head),reference),'REV24D019:referenceDrift');
addpath(genpath(toolbox));
assert(~exist(output_path,'file'),'REV24D019:overwrite');

data=jsondecode(fileread(manifest_path));
assert(strcmp(char(data.protocol),'compstat-rev2-4-objective-cross-eval-v1'));
assert(strcmp(char(data.manifest_sha256), ...
    '35e7c766d3f63cb53aa407c2e6563a34b1a5fd795b982d147475e4c3d409ea95'));
assert(strcmp(char(data.matlab_reference_commit),reference));
assert(strcmp(char(data.release_source_commit_declared),release));
assert(data.trials==128 && data.n_per_model==200);
assert(numel(data.strata)==3);
group=element(data.strata,2);
assert(strcmp(char(group.model),'ehgf_binary'));
assert(strcmp(char(group.observation_model),'unitsq_sgm'));
assert(numel(group.rows)==200);
case019=element(group.rows,20);
assert(strcmp(char(case019.case_id),'REV24-G-ehgf_binary-019'));
assert(strcmp(char(case019.case_sha256), ...
    '276d21f43a91fc8748438aafc6ec44f759f23dc2ae97dae8b4cc1274aba3fefb'));
assert(case019.replicate_zero_based==19);
assert(isequal(double(group.free_indices_zero_based(:)'),[12 13 14]));

u=double(data.inputs(:));
y=double(data.responses(:));
t=(0:127)';
assert(numel(u)==128 && numel(y)==128);
assert(isequal(u,double(mod(37*t+11,101)<51)) && ...
       isequal(y,double(mod(29*t+3,97)<47)),'REV24D019:inputDrift');

pc=ehgf_binary_config();oc=unitsq_sgm_config();
means=[pc.priormus(:)',oc.priormus(:)'];
vars=[pc.priorsas(:)',oc.priorsas(:)'];
assert(isequaln(means,decode_ieee(group.prior_means_full)), ...
    'REV24D019:priorMeans');
assert(isequaln(vars,decode_ieee(group.prior_variances_full_ieee)), ...
    'REV24D019:priorVariances');
full=decode_ieee(case019.full_transformed);
assert(numel(full)==15);
free=double(group.free_indices_zero_based(:)')+1;
assert(isequal(full(free),double(case019.free_transformed(:)')),...
    'REV24D019:originalFreeVector');

r.u=u;r.y=y;r.ign=find(isnan(u))';r.irr=unique([r.ign,find(isnan(y))']);
r.c_prc=pc;r.c_obs=oc;
[traj,states]=pc.prc_fun(r,full(1:14),'trans');
[logp,~,~]=oc.obs_fun(r,states,full(15:end));
assert(isequal(size(states),[128,3,4]) && numel(logp)==128);
fields={'mu','sa','muhat','sahat','v','w','da','psi','epsi','wt','ud'};
statefields={'muhat','sahat','mu','sa'};
d.diagnostic='rev24-ehgf019-latent-trace-v1';
d.source='matlab';
d.source_manifest_sha256=char(data.manifest_sha256);
d.source_case_id=char(case019.case_id);
d.source_case_sha256=char(case019.case_sha256);
d.release_source_commit=release;
d.matlab_reference_commit=reference;
d.trials=128;d.levels=3;
d.matlab_version=version;
d.trial_log_likelihoods=arrayfun(@encode_ieee,logp(:)', 'UniformOutput',false);
d.inferred_states=struct;
for j=1:4
    d.inferred_states.(statefields{j})=encode_matrix(states(:,:,j));
end
d.trajectories=struct;
for j=1:numel(fields)
    assert(isfield(traj,fields{j}), 'REV24D019:missingTraceField');
    d.trajectories.(fields{j})=encode_matrix(traj.(fields{j}));
end
d.original_600_case_grid_modified=false;
d.scientific_gate='NOT_ASSESSED_DIAGNOSTIC_ONLY';
folder=fileparts(output_path);
if ~isempty(folder)&&~exist(folder,'dir');mkdir(folder);end
fid=fopen(output_path,'w');assert(fid>=0,'REV24D019:write');
cleanup=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(d,'PrettyPrint',true));
fprintf('REV-2.4 D019 FROZEN MATLAB TRACE saved, no science PASS.\n');
end

function out=encode_matrix(a)
assert(isnumeric(a) && ndims(a)==2 && size(a,1)==128,...
    'REV24D019:traceDimensions');
out=cell(size(a));
for i=1:numel(a)
    out{i}=encode_ieee(a(i));
end
end

function v=encode_ieee(x)
if isnan(x);v='NaN';
elseif isinf(x)&&x>0;v='+Inf';
elseif isinf(x);v='-Inf';
else;v=double(x);end
end

function out=decode_ieee(x)
if isnumeric(x)
    out=double(x(:)');return;
end
assert(iscell(x),'REV24D019:encoding');
out=zeros(1,numel(x));
for i=1:numel(x)
    v=x{i};
    if ischar(v)||isstring(v)
        switch char(v)
            case 'NaN';out(i)=NaN;
            case '+Inf';out(i)=Inf;
            case '-Inf';out(i)=-Inf;
            otherwise;error('REV24D019:unknownIEEE');
        end
    else
        assert(isnumeric(v)&&isscalar(v),'REV24D019:scalarEncoding');
        out(i)=double(v);
    end
end
end

function item=element(array,i)
if iscell(array);item=array{i};else;item=array(i);end
end
