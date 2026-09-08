function export_m12de_parity(output_path)
%EXPORT_M12DE_PARITY Categorical/world and HHMM frozen MATLAB oracle.
repo_root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root=fullfile(repo_root,'external','hgf-toolbox');
addpath(hgf_root); addpath(fullfile(hgf_root,'core'));
addpath(fullfile(hgf_root,'building_blocks')); addpath(fullfile(hgf_root,'perceptual'));
addpath(fullfile(hgf_root,'utilities'));

payload=struct;
payload.metadata.schema_version='m12de-1';
payload.metadata.reference_version='8.2.0';
payload.metadata.reference_commit='2437f4dc241541072722a2695ddeca7b44d83dd3';

irr=3;

% Categorical
u=[1;2;3;2;1;3;3;1];
r=struct; r.u=u; r.ign=irr; r.c_prc=hgf_categorical_config;
r.c_prc.n_outcomes=3;
l3=log((1/3)/(2/3));
p=[l3 l3 l3 1 1 1 1 .1 1 -4 .05];
[traj,inf]=hgf_categorical(r,p);
payload.cases.hgf_categorical=pack(traj,inf);

r.c_prc=hgf_categorical_norm_config; r.c_prc.n_outcomes=3;
[traj,inf]=hgf_categorical_norm(r,p);
payload.cases.hgf_categorical_norm=pack(traj,inf);

% WhatWorld, reduced to two states for compact deterministic tensor oracle.
uw=[1;2;2;1;2;1;1;2];
r=struct; r.u=uw; r.ign=irr; r.c_prc=hgf_whatworld_config; r.c_prc.n_states=2;
p=[0 0 0 0 1 1 1 1 1 .1 1 -4 .05];
[traj,inf]=hgf_whatworld(r,p);
payload.cases.hgf_whatworld=pack(traj,inf);

% WhichWorld source repair: frozen file references undefined variable da
% while the actual first-level prediction error is da1.
rb=struct; rb.u=[0;1;1;0;1;0;0;1]; rb.ign=irr; rb.c_prc=hgf_whichworld_config;
p=[0 0 1 1 1 .1 1 -4 .05 0 .1];
tmpdir=tempname; mkdir(tmpdir);
src=fileread(fullfile(hgf_root,'perceptual','hgf_whichworld.m'));
src=strrep(src,'lr1(da(2:n,1)==0) = 0;','lr1(da1(2:n,1)==0) = 0;');
fidtmp=fopen(fullfile(tmpdir,'hgf_whichworld.m'),'w'); fwrite(fidtmp,src); fclose(fidtmp);
addpath(tmpdir,'-begin'); clear hgf_whichworld;
[traj,inf]=hgf_whichworld(rb,p);
rmpath(tmpdir); clear hgf_whichworld;
payload.cases.hgf_whichworld=pack(traj,inf);
payload.source_repairs.hgf_whichworld='undefined da repaired to da1 in learning-rate cleanup';

% HHMM source repair: frozen function names do not match tapas_* filenames.
tmpdir=tempname; mkdir(tmpdir);
src=fileread(fullfile(hgf_root,'perceptual','tapas_hhmm_config.m'));
src=strrep(src,'function c = hhmm_config','function c = tapas_hhmm_config');
src=strrep(src,'@hhmm','@tapas_hhmm');
src=strrep(src,'@hhmm_transp','@tapas_hhmm_transp');
fidtmp=fopen(fullfile(tmpdir,'tapas_hhmm_config.m'),'w'); fwrite(fidtmp,src); fclose(fidtmp);

src=fileread(fullfile(hgf_root,'perceptual','tapas_hhmm_transp.m'));
src=strrep(src,'function [pvec, pstruct] = hhmm_transp','function [pvec, pstruct] = tapas_hhmm_transp');
fidtmp=fopen(fullfile(tmpdir,'tapas_hhmm_transp.m'),'w'); fwrite(fidtmp,src); fclose(fidtmp);

src=fileread(fullfile(hgf_root,'perceptual','tapas_hhmm.m'));
src=strrep(src,'function [traj, infStates] = htapas_hmm','function [traj, infStates] = tapas_hhmm');
src=strrep(src,'[p pstruct] = hhmm_transp(r, p);','[p, pstruct] = tapas_hhmm_transp(r, p);');
fidtmp=fopen(fullfile(tmpdir,'tapas_hhmm.m'),'w'); fwrite(fidtmp,src); fclose(fidtmp);
addpath(tmpdir,'-begin'); clear tapas_hhmm tapas_hhmm_config tapas_hhmm_transp;
c=tapas_hhmm_config;
rh=struct; rh.u=[1;2;1;2;2;1;1;2]; rh.ign=irr; rh.c_prc=c;
[traj,inf]=tapas_hhmm(rh,c.priormus,'trans');
rmpath(tmpdir); clear tapas_hhmm tapas_hhmm_config tapas_hhmm_transp;
payload.cases.tapas_hhmm=pack(traj,inf);
payload.hhmm_ptrans=c.priormus;
payload.source_repairs.tapas_hhmm='function/file names aligned and transp call made explicit';

outdir=fileparts(output_path);
if ~isempty(outdir)&&~exist(outdir,'dir'),mkdir(outdir);end
fid=fopen(output_path,'w');
if fid==-1,error('hgfx:m12de:openFailed','Could not open output');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(payload,'PrettyPrint',true));
fprintf('HGFX M12DE MATLAB export: PASS\n');
end

function out=pack(traj,inf)
out=struct; out.traj=traj; out.infStates=inf;
end
