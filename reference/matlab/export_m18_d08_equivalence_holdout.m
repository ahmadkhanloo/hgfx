function export_m18_d08_equivalence_holdout(output_path)
% Prospective D08 holdout frozen by MATLAB_EQUIVALENCE_POLICY.md.
% Do not change seeds, data, model family, starts or tolerances after observing results.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

x = load(fullfile(root,'external','hgf-toolbox','demo','example_usdchf.txt'));
native = [1.04 1 .0001 .1 0 0 1 -13 -2 1e4];
obs_native = .00002;
seeds = [271828182 314159265];

payload.metadata.protocol = 'm18-d08-equivalence-holdout-1';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.numeric_encoding = 'ieee-strings-v1';
payload.metadata.matlab_version = version;
payload.metadata.policy = 'docs/validation/MATLAB_EQUIVALENCE_POLICY.md';
payload.metadata.case_id = 'D08_fit';
payload.model = 'uhgf';
payload.observation = 'gaussian_obs';
payload.native = native;
payload.obs_native = obs_native;
payload.inputs = x;
payload.seeds = seeds;
payload.cases = cell(1,numel(seeds));

for k = 1:numel(seeds)
    c.seed = seeds(k);
    c.success = false;
    c.stage = 'simulation';
    c.error_identifier = '';
    c.error_message = '';
    c.responses = [];
    c.fit = struct;
    try
        s = simModel(x,'uhgf',native,'gaussian_obs',obs_native,c.seed);
        c.responses = s.y;
        c.stage = 'fit';
        pc = uhgf_config();
        oc = gaussian_obs_config();
        fit = fitModel(s.y,x,pc,oc,'quasinewton_optim_config');
        c.fit = strip_fit(fit);
        c.success = true;
        c.stage = 'complete';
    catch ME
        c.error_identifier = ME.identifier;
        c.error_message = ME.message;
    end
    payload.cases{k} = c;
    write_payload(output_path,payload);
    fprintf('M18 D08 holdout seed %d: success=%d stage=%s\n',c.seed,c.success,c.stage);
    clear c
end
end

function out = strip_fit(s)
out.final = s.optim.final;
out.traj = s.traj;
out.prc_priormus = s.c_prc.priormus;
out.prc_priorsas = s.c_prc.priorsas;
out.obs_priormus = s.c_obs.priormus;
out.obs_priorsas = s.c_obs.priorsas;
fields = {'H','Sigma','Corr','negLl','negLj','LME','AIC','BIC','yhat','res','resAC'};
for j = 1:numel(fields)
    out.(fields{j}) = s.optim.(fields{j});
end
if isstruct(s.optim.iter)
    out.iter.x = s.optim.iter.x;
    out.iter.val = s.optim.iter.val;
    out.iter.rst = s.optim.iter.rst;
else
    out.iter = [];
end
end

function write_payload(path,payload)
folder = fileparts(path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
end