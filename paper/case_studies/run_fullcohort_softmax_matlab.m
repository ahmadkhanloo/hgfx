function run_fullcohort_softmax_matlab()
% Independent fixed-parameter M7 softmax on precomputed MATLAB8.2 MAB states.
% The original study fitting and statistical conclusions are NOT reproduced.
root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
oracle=fullfile(root,'external','hgf-toolbox');
addpath(oracle);
addpath(fullfile(oracle,'observation'));
assert(contains(which('softmax'),'external'), 'Wrong observation oracle selected');
folder=fullfile(root,'published_pair_tmp');
manifest=jsondecode(fileread(fullfile(folder,'all_cohort_manifest.json')));
assert(manifest.expected_total_cases==324 && manifest.actual_total_cases==324,'Cohort source mismatch');
records=repmat(struct('id','','status','','reason','','ignored',0),324,1);
fprintf('MATLAB_SOFTMAX_VERSION=%s\n',version);
fprintf('MATLAB_SOFTMAX_ORACLE=%s\n',which('softmax'));
for idx=1:numel(manifest.cases)
    item=manifest.cases(idx);
    records(idx).id=item.id;
    if ~strcmp(item.status,'INPUT_READY')
        records(idx).status='BLOCKED_INPUT'; records(idx).reason=item.status;
        continue;
    end
    try
        input=readmatrix(fullfile(folder,[item.id '_input.txt']),'FileType','text');
        assert(isequal(size(input),[80,2]),'Unexpected source trial matrix');
        u=input(:,1); y=input(:,2);
        assert(all(ismember(u(~isnan(u)),[0 1])),'Invalid source reward');
        assert(all(ismember(y(~isnan(y)),[1 2 3])),'Invalid source choice');
        data=load(fullfile(folder,[item.id '_matlab_result.mat']),'infStates');
        assert(isequal(size(data.infStates),[80 3 3 4]),'Unexpected MATLAB perceptual states');
        r=struct; r.y=y; r.irr=find(isnan(u)|isnan(y)); r.c_obs=softmax_config;
        % Predeclared log(beta)=0, beta=1. Not optimized.
        [logp,yhat,res]=softmax(r,data.infStates,0);
        total_loglik=sum(logp(~isnan(logp)));
        save(fullfile(folder,[item.id '_matlab_softmax.mat']),...
             'logp','yhat','res','total_loglik','-v7');
        records(idx).status='MATLAB_RESPONSE_DONE';
        records(idx).ignored=numel(r.irr);
    catch exc
        records(idx).status='MATLAB_RESPONSE_FAILED';
        records(idx).reason=[exc.identifier ' ' exc.message];
    end
end
status=struct;
status.total=324;
status.pass=sum(strcmp({records.status},'MATLAB_RESPONSE_DONE'));
status.fail=324-status.pass;
status.records=records;
fid=fopen(fullfile(folder,'matlab_softmax_status.json'),'w');
assert(fid~=-1,'Could not write MATLAB status');
fprintf(fid,'%s\n',jsonencode(status));
fclose(fid);
fprintf('MATLAB_SOFTMAX_CASES pass=%d fail=%d total=%d\n',status.pass,status.fail,status.total);
% Never discard failures here; the Python checker must count all 324.
end
