function export_m12_specialized_parity(output_path)
%EXPORT_M12_SPECIALIZED_PARITY Frozen specialized-model forward oracle.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root,'external','hgf-toolbox');
addpath(hgf_root);
addpath(fullfile(hgf_root,'core'));
addpath(fullfile(hgf_root,'building_blocks'));
addpath(fullfile(hgf_root,'perceptual'));
addpath(fullfile(hgf_root,'observation'));
addpath(fullfile(hgf_root,'utilities'));

payload = struct;
payload.metadata.schema_version = 'm12-1';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.numeric_mode = 'CPU float64';

u = [0 1 1 0 1 NaN 0 1 1 0 0 1]';
ign = find(isnan(u))';

% Binary PU
r = base_r(u, ign);
r.c_prc = hgf_binary_pu_config;
p = [NaN 0 1 NaN .1 1 NaN 0 0 1 1 NaN -3 -6 .35 0 1];
[traj, inf] = hgf_binary_pu(r,p);
payload.cases.hgf_binary_pu = pack(traj,inf);

r = base_r(u, ign);
r.c_prc = ehgf_binary_pu_config;
p = [NaN 0 1 NaN .1 1 NaN 0 0 1 1 NaN -3 2 .35 0 1];
[traj, inf] = ehgf_binary_pu(r,p);
payload.cases.ehgf_binary_pu = pack(traj,inf);

r = base_r(u, ign);
r.c_prc = uhgf_binary_pu_config;
p = [NaN 0 1 NaN .1 1 NaN 0 0 1 1 NaN -3 -6 .35 0 1];
[traj, inf] = uhgf_binary_pu(r,p);
payload.cases.uhgf_binary_pu = pack(traj,inf);

% Binary PU-TBT
ut = [u, [.25 .3 .2 .35 .3 .25 .2 .3 .35 .25 .2 .3]'];
r = base_r(ut, ign);
r.c_prc = hgf_binary_pu_tbt_config;
p = [NaN 0 1 NaN .1 1 NaN 0 0 1 1 NaN -5 -6 0 1];
[traj, inf] = hgf_binary_pu_tbt(r,p);
payload.cases.hgf_binary_pu_tbt = pack(traj,inf);

r = base_r(ut, ign);
r.c_prc = ehgf_binary_pu_tbt_config;
p = [NaN 0 1 NaN .1 1 NaN 0 0 1 1 NaN -5 -6 0 1];
[traj, inf] = ehgf_binary_pu_tbt(r,p);
payload.cases.ehgf_binary_pu_tbt = pack(traj,inf);

r = base_r(ut, ign);
r.c_prc = uhgf_binary_pu_tbt_config;
p = [NaN 0 1 NaN .1 1 NaN 0 0 1 1 NaN -5 -6 0 1];
[traj, inf] = uhgf_binary_pu_tbt(r,p);
payload.cases.uhgf_binary_pu_tbt = pack(traj,inf);

% AR1 binary HGF
r = base_r(u, ign);
r.c_prc = hgf_ar1_binary_config;
p = [NaN 0 1 NaN .006 4 NaN 0 .2 NaN 0 1 1 1 NaN -2 -6];
[traj, inf] = hgf_ar1_binary(r,p);
payload.cases.hgf_ar1_binary = pack(traj,inf);

% AR1 binary eHGF
r = base_r(u, ign);
r.c_prc = ehgf_ar1_binary_config;
p = [NaN 0 1 NaN .1 1 NaN 0 .45 NaN 0 1 NaN 0 0 1 1 NaN -3 2];
[traj, inf] = ehgf_ar1_binary(r,p);
payload.cases.ehgf_ar1_binary = pack(traj,inf);

r = base_r(u, ign);
r.c_prc = uhgf_ar1_binary_config;
p = [NaN 0 1 NaN .1 1 NaN 0 .45 NaN 0 1 NaN 0 0 1 1 NaN -3 2];
[traj, inf] = uhgf_ar1_binary(r,p);
payload.cases.uhgf_ar1_binary = pack(traj,inf);

% RW
r = base_r(u, ign);
[traj, inf] = rw_binary(r,[.5 .3]);
payload.cases.rw_binary = pack(traj,inf);

% Dual RW
ud = [0 1 1 0 1 NaN 0 1 1 0 0 1]';
yd = [1 2 1 2 1 2 2 1 2 1 2 1]';
r = base_r(ud, ign);
r.y = yd;
[traj, inf] = rw_binary_dual(r,[.4 .6 .3 .5]);
payload.cases.rw_binary_dual = pack(traj,inf);

% Pearce-Hall
r = base_r(u, ign);
[traj, inf] = ph_binary(r,[.5 .4 .2]);
payload.cases.ph_binary = pack(traj,inf);

% Sutton K1
r = base_r(u, ign);
[traj, inf] = sutton_k1_binary(r,[1 1 .5 .01]);
payload.cases.sutton_k1_binary = pack(traj,inf);

% Scalar Kalman filter
uk = [0.2 0.4 0.3 0.7 0.8 NaN 0.5 0.6 0.55 0.9 0.4 0.3]';
r = base_r(uk, ign);
[traj, inf] = tapas_kf(r,[.2 .3 -2 5]);
payload.cases.kalman = pack(traj,inf);

% HMM (two states, two outcomes)
uh = [1 1 2 2 1 2 2 1 1 2 1 2]';
r = base_r(uh, []);
r.c_prc = tapas_hmm_config;
r.c_prc.n_states = 2;
r.c_prc.n_outcomes = 2;
r.c_prc.B = [.9 .1; .1 .9];
p = [.6 .85 .2];
[traj, inf] = tapas_hmm(r,p);
payload.cases.hmm = pack(traj,inf);

outdir=fileparts(output_path);
if ~isempty(outdir)&&~exist(outdir,'dir'), mkdir(outdir); end
fid=fopen(output_path,'w');
if fid==-1, error('hgfx:m12:openFailed','Could not open %s',output_path); end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(payload,'PrettyPrint',true));
fprintf('HGFX M12 MATLAB specialized export: PASS\n');
end

function r=base_r(u,ign)
r=struct;
r.u=u;
r.ign=ign;
end

function out=pack(traj,inf)
out=struct;
out.traj=traj;
out.infStates=inf;
end
