function export_m12a_ar1_parity(output_path)
%EXPORT_M12A_AR1_PARITY Frozen continuous AR1 HGF oracle.
repo_root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root=fullfile(repo_root,'external','hgf-toolbox');
addpath(hgf_root);
addpath(fullfile(hgf_root,'core'));
addpath(fullfile(hgf_root,'building_blocks'));
addpath(fullfile(hgf_root,'perceptual'));
addpath(fullfile(hgf_root,'utilities'));

payload=struct;
payload.metadata.schema_version='m12a-1';
payload.metadata.reference_version='8.2.0';
payload.metadata.reference_commit='2437f4dc241541072722a2695ddeca7b44d83dd3';

p=[.2 1 .3 .1 .15 0 .2 1 1 -3 -6 .2];

u=[.2 .4 .1 .7 .6 .3 .9 .2]';
r=struct; r.u=u; r.ign=[]; r.c_prc=hgf_ar1_config;
[traj,inf]=hgf_ar1(r,p);
payload.regular.inputs=u;
payload.regular.parameters=p;
payload.regular.traj=traj;
payload.regular.infStates=inf;

ui=[.2 1;.4 .5;.1 1.5;.7 .8;.6 1.2;.3 .6;.9 1.1;.2 .7];
r=struct; r.u=ui; r.ign=4; r.c_prc=hgf_ar1_config; r.c_prc.irregular_intervals=true;
[traj,inf]=hgf_ar1(r,p);
payload.irregular.inputs=ui;
payload.irregular.ignored_matlab=r.ign;
payload.irregular.parameters=p;
payload.irregular.traj=traj;
payload.irregular.infStates=inf;

ptrans=[.2 1 log(.3) log(.1) 0 -Inf .2 1 0 -3 -6 log(.2)];
r=struct; r.u=u; r.ign=[]; r.c_prc=hgf_ar1_config;
[pnative,pstruct]=hgf_ar1_transp(r,ptrans);
payload.transform.ptrans=ptrans;
payload.transform.pnative=pnative;
payload.transform.phi=pstruct.phi;
payload.transform.al=pstruct.al;

outdir=fileparts(output_path);
if ~isempty(outdir)&&~exist(outdir,'dir'),mkdir(outdir);end
fid=fopen(output_path,'w');
if fid==-1,error('hgfx:m12a:openFailed','Could not open output');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(payload,'PrettyPrint',true));
fprintf('HGFX M12A AR1 export: PASS\n');
end
