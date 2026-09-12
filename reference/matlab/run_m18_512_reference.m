function run_m18_512_reference(case_dir, output_dir)
%RUN_M18_512_REFERENCE Run frozen MATLAB HGF on the exact HGFX 512-trial case.
%
% The case must first be exported by:
%   python scripts/export_m18_512_reference_case.py
%
% This runner deliberately consumes the exported native parameters and input
% sequence. It does not resample, change the model family, or relax the case.

if nargin < 1
    case_dir = fullfile('reference', 'generated', 'm18_512_hgf');
end
if nargin < 2
    output_dir = fullfile(case_dir, 'matlab');
end

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

expected_commit = strtrim(fileread(fullfile(repo_root, 'reference', 'HGF_COMMIT')));
expected_version = strtrim(fileread(fullfile(repo_root, 'reference', 'HGF_VERSION')));
if ~exist(output_dir, 'dir'); mkdir(output_dir); end

meta = read_json(fullfile(case_dir, 'metadata.json'));
inp = read_json(fullfile(case_dir, 'input.json'));
pars = read_json(fullfile(case_dir, 'parameters.json'));

u = double(inp.u(:));
prc_native = double(pars.perceptual_native(:)');
obs_native = double(pars.observation_native(:)');

result = struct();
result.status = 'ERROR';
result.error_identifier = '';
result.error_message = '';
result.hgf_version = expected_version;
result.hgf_commit_sha = expected_commit;
result.matlab_version = version;
result.model = meta.model;
result.observation_model = meta.observation_model;
result.trial_count = meta.trial_count;
result.dataset_seed = meta.dataset_seed;

try
    % tapas_simModel is the MATLAB toolbox simulation entry point. Use the
    % exact model/observation family represented by the frozen case.
    sim = tapas_simModel(u, 'tapas_hgf_binary', prc_native, ...
        'tapas_unitsq_sgm', obs_native, meta.simulation_seed);
    result.status = 'OK';
    result.y = sim.y;
    if isfield(sim, 'traj'); result.traj = sim.traj; end
    if isfield(sim, 'p_prc'); result.p_prc = sim.p_prc; end
    if isfield(sim, 'p_obs'); result.p_obs = sim.p_obs; end
catch ME
    result.error_identifier = ME.identifier;
    result.error_message = ME.message;
end

write_json(fullfile(output_dir, 'result.json'), result);
fprintf('M18 512 MATLAB reference status=%s\n', result.status);
if strcmp(result.status, 'ERROR')
    error('hgfx:m18:matlabReferenceFailed', '%s: %s', ...
        result.error_identifier, result.error_message);
end
end

function value = read_json(path)
value = jsondecode(fileread(path));
end

function write_json(path, value)
fid = fopen(path, 'w');
if fid == -1
    error('hgfx:fixture:openFailed', 'Could not open %s for writing.', path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(value, 'PrettyPrint', true));
end
