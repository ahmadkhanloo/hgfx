function export_m12bc_parity(output_path)
%EXPORT_M12BC_PARITY MAB and JGET frozen MATLAB oracle.
repo_root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root=fullfile(repo_root,'external','hgf-toolbox');
addpath(hgf_root);
addpath(fullfile(hgf_root,'core'));
addpath(fullfile(hgf_root,'building_blocks'));
addpath(fullfile(hgf_root,'perceptual'));
addpath(fullfile(hgf_root,'utilities'));

payload=struct;
payload.metadata.schema_version='m12bc-1';
payload.metadata.reference_version='8.2.0';
payload.metadata.reference_commit='2437f4dc241541072722a2695ddeca7b44d83dd3';

ub=[0 1 1 0 1 NaN 0 1 1 0 0 1]';
choices=[1 2 3 1 2 3 1 2 3 1 2 3]';

% Binary MAB
r=struct; r.u=[ub choices]; r.y=choices; r.ign=6; r.c_prc=hgf_binary_mab_config;
r.c_prc.n_bandits=3; r.c_prc.coupled=false;
p=[NaN 0 1 NaN .1 1 NaN 0 0 1 1 NaN -3 -6];
[traj,inf]=hgf_binary_mab(r,p);
payload.cases.hgf_binary_mab=pack(traj,inf);

% Continuous AR1 MAB
% Frozen source defect: hgf_ar1_mab.m prepends a dummy choice to y but never
% removes it before sub2ind-based psi extraction. Run an exact temporary copy
% with the minimal source repair y(1)=[] after dau(1)=[].
uc=[.2 .4 .1 .7 .6 NaN .3 .9 .2 .5 .8 .4]';
r=struct; r.u=[uc choices]; r.y=[]; r.ign=6; r.c_prc=hgf_ar1_mab_config;
r.c_prc.n_bandits=3;
p=[.2 1 .3 .1 .1 0 .2 1 1 -3 -6 .2];
tmpdir=tempname; mkdir(tmpdir);
src=fileread(fullfile(hgf_root,'perceptual','hgf_ar1_mab.m'));
src=strrep(src,'dau(1)       = [];',sprintf('dau(1)       = [];\ny(1)         = [];'));
fidtmp=fopen(fullfile(tmpdir,'hgf_ar1_mab.m'),'w'); fwrite(fidtmp,src); fclose(fidtmp);
addpath(tmpdir,'-begin'); clear hgf_ar1_mab;
[traj,inf]=hgf_ar1_mab(r,p);
rmpath(tmpdir); clear hgf_ar1_mab;
payload.cases.hgf_ar1_mab=pack(traj,inf);
payload.source_repairs.hgf_ar1_mab='frozen source: remove dummy y before psi indexing';

% AR1 binary MAB HGF
r=struct; r.u=[ub choices]; r.y=choices; r.ign=6; r.c_prc=hgf_ar1_binary_mab_config;
r.c_prc.n_bandits=3; r.c_prc.coupled=false;
p=[NaN 0 1 NaN .1 1 NaN 0 .2 NaN 0 1 1 1 NaN -2 -6];
[traj,inf]=hgf_ar1_binary_mab(r,p);
payload.cases.hgf_ar1_binary_mab=pack(traj,inf);

% eHGF AR1 binary MAB
r=struct; r.u=[ub choices]; r.y=choices; r.ign=6; r.c_prc=ehgf_ar1_binary_mab_config;
r.c_prc.n_bandits=3; r.c_prc.coupled=false;
p=[NaN 0 1 NaN .1 1 NaN 0 .45 NaN 0 1 NaN 0 0 1 1 NaN -3 2];
[traj,inf]=ehgf_ar1_binary_mab(r,p);
payload.cases.ehgf_ar1_binary_mab=pack(traj,inf);

% uHGF AR1 binary MAB
r=struct; r.u=[ub choices]; r.y=choices; r.ign=6; r.c_prc=uhgf_ar1_binary_mab_config;
r.c_prc.n_bandits=3; r.c_prc.coupled=false;
[traj,inf]=uhgf_ar1_binary_mab(r,p);
payload.cases.uhgf_ar1_binary_mab=pack(traj,inf);

% JGET variants
uj=[.2 .4 .1 .7 .6 NaN .3 .9 .2 .5 .8 .4]';
pj=[.3 1 .5 .2 -2 -2 1 1 1 1 1 0 -3 -6 -3 -6];

r=struct; r.u=uj; r.ign=6; r.c_prc=hgf_jget_config;
[traj,inf]=hgf_jget(r,pj);
payload.cases.hgf_jget=pack(traj,inf);

r.c_prc=ehgf_jget_config;
[traj,inf]=ehgf_jget(r,pj);
payload.cases.ehgf_jget=pack(traj,inf);

r.c_prc=uhgf_jget_config;
[traj,inf]=uhgf_jget(r,pj);
payload.cases.uhgf_jget=pack(traj,inf);

outdir=fileparts(output_path);
if ~isempty(outdir)&&~exist(outdir,'dir'),mkdir(outdir);end
fid=fopen(output_path,'w');
if fid==-1,error('hgfx:m12bc:openFailed','Could not open output');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(payload,'PrettyPrint',true));
fprintf('HGFX M12BC MATLAB export: PASS\n');
end

function out=pack(traj,inf)
out=struct; out.traj=traj; out.infStates=inf;
end
