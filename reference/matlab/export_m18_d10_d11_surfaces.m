function export_m18_d10_d11_surfaces(output_path)
% Frozen D10/D11 surface-data reference, protocol v2.
% This gate intentionally uses a deterministic fit-like struct because the
% MATLAB plotting utilities consume result fields only; no fitting/simulation
% is part of the surface contract.

root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));

est = struct;
est.u = (1:5)';
est.c_prc.priorsas = [1 0 2];
est.c_obs.priorsas = 0.5;

% Preserve MATLAB struct field order used by fit_plotCorr label expansion.
est.p_prc.mu = [0.1 0.2];
est.p_prc.omega = -1;
est.p_prc.p = [0.1 0.2 -1];
est.p_prc.ptrans = [0.1 0.2 -1];
est.p_obs.ze = 0.05;
est.p_obs.p = 0.05;
est.p_obs.ptrans = log(0.05);

est.optim.Corr = [1 0.25 -0.1; 0.25 1 0.4; -0.1 0.4 1];
est.optim.Sigma = [2 0.5 -0.1; 0.5 3 0.6; -0.1 0.6 1.5];
est.optim.res = [0.10; -0.20; 0.30; -0.10; 0.05];
est.optim.resAC = [0.20; 0.30; 1.00; 0.30; 0.20];
est.optim.yhat = [0.20; 0.40; 0.60; 0.80; 0.50];

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

payload.protocol = 'm18-d10-d11-surfaces-2';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D10_D11_surfaces';
payload.fixture_id = 'synthetic_fit_v2';
payload.est = est;
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
fprintf('M18 D10/D11 surface reference v2 exported.\n');
end
