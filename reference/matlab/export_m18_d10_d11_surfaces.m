function export_m18_d10_d11_surfaces(output_path)
% Frozen D10/D11 surface-data reference. Pixel rendering is not gated.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

u = load(fullfile(root,'external','hgf-toolbox','demo','example_binary_input.txt'));
seed = 123;
native = [NaN 0 1 NaN 1 1 NaN 0 0 NaN 1 NaN -2.5 -6];
sim = simModel(u,'hgf_binary',native,'unitsq_sgm',5,seed);
est = fitModel(sim.y,sim.u,'hgf_binary_config','unitsq_sgm_config','quasinewton_optim_config');

prc_ind = est.c_prc.priorsas;
prc_ind(isnan(prc_ind)) = 0;
prc_ind = find(prc_ind);
obs_ind = est.c_obs.priorsas;
obs_ind(isnan(obs_ind)) = 0;
obs_ind = find(obs_ind);

names_prc = fieldnames(est.p_prc);
fields_prc = struct2cell(est.p_prc);
expanded_prc = {};
for k = 1:length(names_prc)
    for l = 1:numel(fields_prc{k})
        expanded_prc{end+1,1} = names_prc{k}; %#ok<AGROW>
    end
end
expanded_prc = expanded_prc(1:length(est.p_prc.p));

names_obs = fieldnames(est.p_obs);
fields_obs = struct2cell(est.p_obs);
expanded_obs = {};
for k = 1:length(names_obs)
    for l = 1:numel(fields_obs{k})
        expanded_obs{end+1,1} = names_obs{k}; %#ok<AGROW>
    end
end
expanded_obs = expanded_obs(1:length(est.p_obs.p));
labels = [expanded_prc(prc_ind); expanded_obs(obs_ind)];

resAC_shifted = fftshift(est.optim.resAC);
n = size(resAC_shifted,1);
upperend = n - ceil((n+1)/2);
lowerend = upperend-n+1;
lags = (lowerend:upperend)';

payload.protocol = 'm18-d10-d11-surfaces-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D10_D11_surfaces';
payload.seed = seed;
payload.est.u = est.u;
payload.est.c_prc.priorsas = est.c_prc.priorsas;
payload.est.c_obs.priorsas = est.c_obs.priorsas;
payload.est.p_prc = est.p_prc;
payload.est.p_obs = est.p_obs;
payload.est.optim.Corr = est.optim.Corr;
payload.est.optim.Sigma = est.optim.Sigma;
payload.est.optim.res = est.optim.res;
payload.est.optim.resAC = est.optim.resAC;
payload.est.optim.yhat = est.optim.yhat;
payload.d10.labels = labels;
payload.d10.Corr = est.optim.Corr;
payload.d10.Sigma = est.optim.Sigma;
payload.d11.res = est.optim.res;
payload.d11.resAC_shifted = resAC_shifted;
payload.d11.lags = lags;
payload.d11.yhat = est.optim.yhat;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D10/D11 surface reference exported.\n');
end
