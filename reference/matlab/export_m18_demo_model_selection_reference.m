function export_m18_demo_model_selection_reference(output_path)
%EXPORT_M18_DEMO_MODEL_SELECTION_REFERENCE Freeze the official eHGF challenge.
%
% The frozen HGF 8.2.0 demo explicitly states that the parameter regime below
% fails in the classic HGF while eHGF handles it. This exporter records the
% actual frozen-reference behavior on the official 320-trial demo input.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

expected_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
demo_dir = fullfile(hgf_root, 'demo');
u = load(fullfile(demo_dir, 'example_binary_input.txt'));

% Native-space vector copied from the frozen official hgf_demo.m eHGF section.
p_native = [NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3];

payload = struct;
payload.metadata.schema_version = 'm18-demo-model-selection-1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = expected_commit;
payload.metadata.matlab_version = version;
payload.metadata.numeric_mode = 'CPU float64';
payload.metadata.demo_source = 'demo/hgf_demo.m';
payload.metadata.demo_input = 'demo/example_binary_input.txt';
payload.metadata.case_id = 'D02_EHGF_CLASSIC_HGF_FAILURE_REGIME';
payload.metadata.scientific_rule = ['classic HGF is expected to reject this parameter ', ...
    'region; eHGF is expected to run successfully'];
payload.inputs = u;
payload.native_parameters = p_native;
payload.hgf_binary = run_variant(u, p_native, 'hgf');
payload.ehgf_binary = run_variant(u, p_native, 'ehgf');

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m18demo:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M18 demo model-selection MATLAB reference export: COMPLETE\n');
end

function out = run_variant(inputs, p_native, update_type)
r = struct;
r.u = inputs;
r.ign = find(isnan(r.u(:,1)))';
r.c_prc = hgf_binary_config;
r.c_prc.irregular_intervals = false;
r.c_prc.update_type = update_type;

out = struct;
out.update_type = update_type;
try
    if strcmp(update_type, 'hgf')
        [traj, infStates] = hgf_binary(r, p_native);
    elseif strcmp(update_type, 'ehgf')
        [traj, infStates] = ehgf_binary(r, p_native);
    else
        error('hgfx:m18demo:unsupportedVariant', 'Unsupported update type %s', update_type);
    end
    out.success = true;
    out.error_identifier = '';
    out.error_message = '';
    out.traj = traj;
    out.inf_states = infStates;
catch ME
    out.success = false;
    out.error_identifier = ME.identifier;
    out.error_message = ME.message;
    out.traj = struct;
    out.inf_states = [];
end
end
