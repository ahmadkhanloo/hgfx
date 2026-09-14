function export_m18_d08_endpoint(output_path)
% Focused D08 uHGF endpoint-sensitivity and optimizer-trace evidence.
% Diagnostic only; no acceptance threshold, seed, data or model is changed.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

x = load(fullfile(root,'external','hgf-toolbox','demo','example_usdchf.txt'));
native = [1.04 1 .0001 .1 0 0 1 -13 -2 1e4];
obs_native = .00002;
seed = 123456789;

s = simModel(x,'uhgf',native,'gaussian_obs',obs_native,seed);
pc = uhgf_config();
oc = gaussian_obs_config();
fit = fitModel(s.y,x,pc,oc,'quasinewton_optim_config');

payload.protocol = 'm18-d08-endpoint-diagnostic-2';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D08_fit';
payload.model = 'uhgf';
payload.observation = 'gaussian_obs';
payload.seed = seed;
payload.inputs = x;
payload.responses = s.y;
payload.native = native;
payload.obs_native = obs_native;
payload.final = fit.optim.final;
payload.negLl = fit.optim.negLl;
payload.negLj = fit.optim.negLj;
payload.LME = fit.optim.LME;
payload.prc_priorsas = fit.c_prc.priorsas;
payload.obs_priorsas = fit.c_obs.priorsas;
payload.traj.psi = fit.traj.psi;
payload.traj.da = fit.traj.da;
payload.traj.dau = fit.traj.dau;
payload.traj.epsi = fit.traj.epsi;
if isstruct(fit.optim.iter)
    payload.trace.x = fit.optim.iter.x;
    payload.trace.val = fit.optim.iter.val;
    payload.trace.rst = fit.optim.iter.rst;
else
    payload.trace = [];
end

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D08 endpoint diagnostic exported: %s\n', output_path);
end
