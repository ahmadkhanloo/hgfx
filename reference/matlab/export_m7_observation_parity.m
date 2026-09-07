function export_m7_observation_parity(output_path)
repo_root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(repo_root,'external','hgf-toolbox')));
payload=struct;
payload.metadata.schema_version='m7-1';
payload.metadata.reference_version='8.2.0';
payload.metadata.reference_commit='2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.numeric_mode='CPU float64';
n=8; irr=4;
s=zeros(n,3,4); x=linspace(.15,.85,n)';
s(:,1,1)=x; s(:,1,2)=x.*(1-x); s(:,1,3)=min(max(x+.03,.05),.95); s(:,1,4)=.2;
s(:,2,1)=linspace(-.8,.8,n)'; s(:,2,2)=.35; s(:,2,3)=linspace(-.7,.9,n)'; s(:,2,4)=linspace(.2,.5,n)';
s(:,3,1)=linspace(-2.4,-1.4,n)'; s(:,3,2)=.5; s(:,3,3)=linspace(-2.2,-1.2,n)'; s(:,3,4)=.6;
yb=[0 1 1 0 1 0 1 1]'; u=yb; yc=linspace(.1,.9,n)'; yg=linspace(6.1,6.8,n)';

r=base_r(yb,u,irr); r.c_obs.predorpost=1; r.c_prc.model='hgf_binary';
payload.cases.unitsq_sgm=pack(unitsq_sgm(r,s,log(12)));
payload.cases.unitsq_sgm_mu3=pack(unitsq_sgm_mu3(r,s,[]));
payload.cases.softmax_binary=pack(softmax_binary(r,s,log(2)));
payload.cases.cdfgaussian_obs=pack(cdfgaussian_obs(r,s,[]));

r=base_r(yc,u,irr); r.c_obs.predorpost=1; r.c_prc.model='hgf_binary';
payload.cases.beta_obs=pack(beta_obs(r,s,log(8)));

r=base_r(yg,u,irr);
payload.cases.gaussian_obs=pack(gaussian_obs(r,s,log(.4)));
payload.cases.gaussian_obs_offset=pack(gaussian_obs_offset(r,s,[log(.4) 6]));
payload.cases.logrt_linear_binary=pack(logrt_linear_binary(r,s,[6.2 .2 -.3 .4 -.1 log(.2)]));
payload.cases.logrt_linear_binary_minimal=pack(logrt_linear_binary_minimal(r,s,[6.2 .2 -.3 log(.2)]));

nc=3; sc=zeros(n,3,nc,4);
for k=1:n
 for c=1:nc
  sc(k,1,c,1)=-.4+.25*(c-1)+.03*(k-1);
  sc(k,1,c,3)=-.3+.22*(c-1)+.02*(k-1);
 end
end
sc(:,3,1,3)=linspace(-1,.2,n)';
ym=[1 2 3 1 3 2 1 2]'; um=[1 0 1 0 1 0 1 0]';
r=base_r(ym,um,irr); r.c_obs.predorpost=1;
payload.cases.softmax=pack(softmax(r,sc,log(1.7)));
payload.cases.softmax_mu3=pack(softmax_mu3(r,sc,[]));

s5=zeros(n,1,nc,1,2); s5(:,1,:,1,1)=sc(:,1,:,1); s5(:,1,:,1,2)=sc(:,1,:,3);
r=base_r(ym,um,irr); r.c_obs.predorpost=2;
payload.cases.softmax_2beta=pack(softmax_2beta(r,s5,[log(1.5) log(.8)]));

outdir=fileparts(output_path); if ~isempty(outdir)&&~exist(outdir,'dir'), mkdir(outdir); end
fid=fopen(output_path,'w'); if fid==-1, error('hgfx:m7:openFailed','Could not open %s',output_path); end
cleanup=onCleanup(@() fclose(fid)); fprintf(fid,'%s\n',jsonencode(payload,'PrettyPrint',true));
fprintf('HGFX M7 MATLAB observation export: PASS\n');
end

function r=base_r(y,u,irr)
r=struct; r.y=y; r.u=u; r.irr=irr; r.c_obs=struct('predorpost',1); r.c_prc=struct('model','hgf_binary');
end

function out=pack(varargin)
if nargin==1 && iscell(varargin{1}), vals=varargin{1}; else, vals=varargin; end
if numel(vals)==1
 error('hgfx:m7:packUsage','pack requires three observation outputs');
end
logp=vals{1}; yhat=vals{2}; res=vals{3};
out=struct('logp',logp,'yhat',yhat,'res',res,'total_loglik',sum(logp(~isnan(logp))));
end
