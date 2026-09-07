function export_fixture(output_dir)
%EXPORT_FIXTURE Export the first HGFX golden reference fixture.
%
% This M1 bootstrap case intentionally uses the frozen HGF utility
% utilities/tapas_logit.m. Later fixture families reuse the same JSON contract.

if nargin < 1
    output_dir = fullfile('reference', 'generated', 'm1_tapas_logit');
end

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

expected_commit = strtrim(fileread(fullfile(repo_root, 'reference', 'HGF_COMMIT')));
expected_version = strtrim(fileread(fullfile(repo_root, 'reference', 'HGF_VERSION')));

if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

x = [0.1, 0.2, 0.5, 0.8, 0.9];
a = 1.0;
y = tapas_logit(x, a);

metadata = struct( ...
    'hgf_version', expected_version, ...
    'hgf_commit_sha', expected_commit, ...
    'matlab_version', version, ...
    'fixture_schema_version', 1, ...
    'model_name', 'utility:tapas_logit', ...
    'response_model_name', 'N/A', ...
    'optimizer_name', 'N/A', ...
    'rng_seed', 0);

config = struct('function', 'tapas_logit', 'a', a);
input_payload = struct('x', x);
expected_payload = struct('y', y);

write_json(fullfile(output_dir, 'metadata.json'), metadata);
write_json(fullfile(output_dir, 'config.json'), config);
write_json(fullfile(output_dir, 'input.json'), input_payload);
write_json(fullfile(output_dir, 'expected.json'), expected_payload);

fprintf('HGFX M1 MATLAB export: PASS\n');
fprintf('output_dir=%s\n', output_dir);
end


function write_json(path, value)
fid = fopen(path, 'w');
if fid == -1
    error('hgfx:fixture:openFailed', 'Could not open %s for writing.', path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(value, 'PrettyPrint', true));
end
