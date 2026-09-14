function export_m18_d09_official_samplemodel(output_path)
% Frozen official D09 sampleModel paired oracle.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
u = load(fullfile(root,'external','hgf-toolbox','demo','example_binary_input.txt'));
seeds = [123 456];

payload.protocol = 'm18-d09-official-samplemodel-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.matlab_version = version;
payload.inputs = u;
payload.seeds = seeds;
payload.cases = cell(1,numel(seeds));

for k = 1:numel(seeds)
    seed = seeds(k);
    c_prc = hgf_binary_config;
    c_obs = unitsq_sgm_config;
    % Reproduce sampleModel's seeded standard-normal parameter draw sequence.
    rng(seed);
    z_prc = randn(1,length(c_prc.priorsas));
    z_obs = randn(1,length(c_obs.priorsas));
    sam = sampleModel(u,c_prc,c_obs,seed);
    item.seed = seed;
    item.prc_standard_normals = z_prc;
    item.obs_standard_normals = z_obs;
    item.p_prc_trans = sam.p_prc.ptrans;
    item.p_prc = sam.p_prc.p;
    item.p_obs_trans = sam.p_obs.ptrans;
    item.p_obs = sam.p_obs.p;
    item.traj = sam.traj;
    item.responses = sam.y;
    item.ignored_matlab = sam.ign;
    item.c_sim_seed = sam.c_sim.seed;
    payload.cases{k} = item;
end

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D09 official sampleModel export: %d cases\n',numel(seeds));
end
