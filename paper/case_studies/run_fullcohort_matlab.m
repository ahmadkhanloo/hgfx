function run_fullcohort_matlab()
% Full prospective published-data input grid, no optimizer or patient inference.
root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
oracle=fullfile(root,'external','hgf-toolbox');
addpath(oracle);
addpath(fullfile(oracle,'core'));
addpath(fullfile(oracle,'building_blocks'));
addpath(fullfile(oracle,'perceptual'));
addpath(fullfile(oracle,'utilities'));
assert(contains(which('hgf_ar1_binary_mab'),'external'), 'Pinned HGF Toolbox not selected');
folder=fullfile(root,'published_pair_tmp');
source=jsondecode(fileread(fullfile(folder,'all_cohort_manifest.json')));
assert(source.expected_total_cases==326 && source.actual_total_cases==326, 'Mismatch in frozen cohort denominator');
p=[NaN 0 1 NaN 0.1 1 NaN 0 0.2 NaN 0 1 1 1 NaN -2 -6];
records=repmat(struct('id','','status','','reason','','num_ignored',0),326,1);
fprintf('MATLAB_RELEASE=%s\n',version);
fprintf('MATLAB_ORACLE=%s\n',which('hgf_ar1_binary_mab'));
for idx=1:numel(source.cases)
    entry=source.cases(idx);
    records(idx).id=entry.id;
    if ~strcmp(entry.status,'INPUT_READY')
        records(idx).status='BLOCKED_INPUT';
        records(idx).reason=entry.status;
        continue;
    end
    try
        vec=readmatrix(fullfile(folder,[entry.id '_input.txt']),'FileType','text');
        assert(isequal(size(vec),[80 2]),'Data size mismatch');
        u=vec(:,1);y=vec(:,2);
        assert(all(ismember(u(~isnan(u)),[0 1])),'Unexpected native outcomes');
        assert(all(ismember(y(~isnan(y)),[1 2 3])),'Unexpected native choices');
        r=struct;
        r.u=[u y];
        r.y=y;
        r.ign=find(isnan(u)|isnan(y));
        r.c_prc=hgf_ar1_binary_mab_config;
        r.c_prc.n_bandits=3;
        r.c_prc.coupled=false;
        r.c_prc.irregular_intervals=false;
        [traj,infStates]=hgf_ar1_binary_mab(r,p);
        save(fullfile(folder,[entry.id '_matlab_result.mat']),'traj','infStates','-v7');
        records(idx).status='MATLAB_FORWARD_DONE';
        records(idx).num_ignored=numel(r.ign);
    catch e
        records(idx).status='MATLAB_FAILED';
        records(idx).reason=e.identifier;
    end
end
status=struct;
status.total_cases=326;
status.successes=sum(strcmp({records.status},'MATLAB_FORWARD_DONE'));
status.failures=326-status.successes;
status.records=records;
fid=fopen(fullfile(folder,'matlab_all_cohort_status.json'),'w');
assert(fid~=-1,'Cannot write status');
fprintf(fid,'%s\n',jsonencode(status));
fclose(fid);
fprintf('MATLAB_ALL_COHORT_DONE successful=%d failed=%d total=%d\n',status.successes,status.failures,status.total_cases);
% Do NOT reject failures here: Python must include them in the full denominator.
end
