function export_m12fg_parity(output_path)
%EXPORT_M12FG_PARITY Auxiliary perceptual and remaining observation families.
repo_root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root=fullfile(repo_root,'external','hgf-toolbox');
addpath(hgf_root); addpath(fullfile(hgf_root,'core'));
addpath(fullfile(hgf_root,'building_blocks')); addpath(fullfile(hgf_root,'perceptual'));
addpath(fullfile(hgf_root,'observation')); addpath(fullfile(hgf_root,'utilities'));

payload=struct;
payload.metadata.schema_version='m12fg-1';
payload.metadata.reference_version='8.2.0';
payload.metadata.reference_commit='2437f4dc241541072722a2695ddeca7b44d83dd3';

n=8; irr=3;
u=[0;1;0;1;1;0;1;0];
y=[0.011;0.012;0.013;0.014;0.015;0.016;0.017;0.018];

base=NaN(n,3,4);
base(:,1,1)=linspace(.2,.8,n);
base(:,1,2)=linspace(.15,.25,n);
base(:,2,1)=linspace(-1,1,n);
base(:,2,2)=linspace(.3,.5,n);
base(:,3,1)=linspace(-2,1,n);
base(:,3,2)=linspace(.4,.7,n);

r=struct; r.u=u; r.y=y; r.irr=irr;

[a,b,c]=bayes_optimal(r,base,[]); payload.bayes_optimal=pack3(a,b,c);
[a,b,c]=bayes_optimal_binary(r,base,[]); payload.bayes_optimal_binary=pack3(a,b,c);
[a,b,c]=squared_pe(r,base,log(.2)); payload.squared_pe=pack3(a,b,c);

prs=log([.0052 .0052 .0006 .001]);
[a,b,c]=rs_belief(r,base,prs); payload.rs_belief=pack3(a,b,c);
[a,b,c]=rs_precision(r,base,prs); payload.rs_precision=pack3(a,b,c);
[a,b,c]=rs_surprise(r,base,prs); payload.rs_surprise=pack3(a,b,c);

% categorical Bayes-optimal
cat=NaN(n,1,3,1);
for k=1:n
    cat(k,1,:,1)=[.2 .3 .5];
end
rc=struct; rc.u=[1;2;3;1;3;2;1;3]; rc.y=[]; rc.irr=irr;
[a,b,c]=bayes_optimal_categorical(rc,cat,[]);
payload.bayes_optimal_categorical=pack3(a,b,c);

% WhichWorld Bayes-optimal uses four worlds
wwh=NaN(n,1,4,1,1);
for k=1:n
    wwh(k,1,:,1,1)=[.1 .2 .3 .4];
end
rw=struct; rw.u=u; rw.y=[]; rw.irr=irr;
[a,b,c]=bayes_optimal_whichworld(rw,wwh,[]);
payload.bayes_optimal_whichworld=pack3(a,b,c);

% WhatWorld Bayes-optimal + precision response
ns=2;
wht=NaN(n,2,ns,ns,1,2);
for k=1:n
    wht(k,1,:,:,1,1)=[.7 .4;.3 .6];
    wht(k,1,:,:,1,2)=[.2 .3;.25 .35];
    wht(k,2,:,:,1,1)=[.5 -.5;.7 -.7];
end
rwt=struct; rwt.u=[1;2;1;2;2;1;2;1]; rwt.y=y; rwt.irr=irr;
rwt.c_prc=struct; rwt.c_prc.n_states=ns;
tmpdir=tempname; mkdir(tmpdir);
src=fileread(fullfile(hgf_root,'perceptual','bayes_optimal_whatworld.m'));
src=strrep(src,'pred(r.irr,:) = [];','pred(r.irr,:,:) = [];');
fidtmp=fopen(fullfile(tmpdir,'bayes_optimal_whatworld.m'),'w'); fwrite(fidtmp,src); fclose(fidtmp);
addpath(tmpdir,'-begin'); clear bayes_optimal_whatworld;
[a,b,c]=bayes_optimal_whatworld(rwt,wht,[]);
rmpath(tmpdir); clear bayes_optimal_whatworld;
payload.bayes_optimal_whatworld=pack3(a,b,c);
payload.source_repairs.bayes_optimal_whatworld='preserve 3-D prediction tensor when deleting irregular trials';
[a,b,c]=rs_precision_whatworld(rwt,wht,log([.0052 .0006 .001]));
payload.rs_precision_whatworld=pack3(a,b,c);

% Conditioned hallucination observation families
ch_inputs=[u [0;.25;.5;.75;0;.25;.5;.75]];
rch=struct; rch.u=ch_inputs; rch.y=[0;1;1;0;1;0;1;1]; rch.irr=irr;
[a,b,c]=condhalluc_obs(rch,base,log(48)); payload.condhalluc_obs=pack3(a,b,c);
[a,b,c]=condhalluc_obs2(rch,base,[log(48) log(1)]); payload.condhalluc_obs2=pack3(a,b,c);
[a,b,c]=condhalluc_obs3(rch,base,log(48)); payload.condhalluc_obs3=pack3(a,b,c);

% World observation states: n x levels x choices x channels
nc=3;
sw=NaN(n,3,nc,4);
for k=1:n
    sw(k,1,:,1)=[.2 .5 .3] + .01*k;
    sw(k,1,:,3)=[.25 .45 .30] + .01*k;
    sw(k,3,1,3)=-1 + .1*k;
end
rsw=struct; rsw.u=[u [1;2;3;1;2;3;1;2]]; rsw.y=[1;2;3;1;2;3;1;2]; rsw.irr=irr;
rsw.c_obs=struct; rsw.c_obs.predorpost=1;
[a,b,c]=softmax_wld(rsw,sw,[log(1.3) .2 -.1]); payload.softmax_wld=pack3(a,b,c);
[a,b,c]=softmax_mu3_wld(rsw,sw,[.2 -.1]); payload.softmax_mu3_wld=pack3(a,b,c);

% WhatWorld logRT uses n x levels x to x from x channels.
lrt=NaN(n,3,ns,ns,4);
for k=1:n
    lrt(k,1,:,:,1)=[.7 .4;.3 .6];
    lrt(k,1,:,:,3)=[1 0;0 0];
    if mod(k,2)==0, lrt(k,1,:,:,3)=[0 0;1 0]; end
    lrt(k,2,:,:,3)=[.4 -.4;.6 -.6];
    lrt(k,2,:,:,4)=[.25 .3;.35 .4];
    lrt(k,3,1,1,3)=-1+.05*k;
end
rl=struct; rl.u=rwt.u; rl.y=log([500;520;510;530;540;525;535;515]); rl.irr=irr;
[a,b,c]=logrt_linear_whatworld(rl,lrt,[log(500) .1 -.05 .02 log(.2)]);
payload.logrt_linear_whatworld=pack3(a,b,c);

outdir=fileparts(output_path);
if ~isempty(outdir)&&~exist(outdir,'dir'),mkdir(outdir);end
fid=fopen(output_path,'w');
if fid==-1,error('hgfx:m12fg:openFailed','Could not open output');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(payload,'PrettyPrint',true));
fprintf('HGFX M12FG MATLAB export: PASS\n');
end

function s=pack3(a,b,c)
s=struct; s.logp=a; s.yhat=b; s.res=c;
end
