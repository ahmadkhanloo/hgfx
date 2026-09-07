function export_m2_parity(output_path)
%EXPORT_M2_PARITY Export frozen MATLAB config/data semantics for HGFX M2.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

payload = struct;
payload.hgf_binary = export_config(hgf_binary_config, @hgf_binary_transp);
payload.hgf = export_config(hgf_config, @hgf_transp);
payload.unitsq_sgm = export_config(unitsq_sgm_config, @unitsq_sgm_transp);

inputs = (1:25)' ./ 25;
window = inputs(1:20,1);
v = var(window, 1);
payload.placeholders = struct( ...
    'p99991', inputs(1,1), ...
    'p99992', v, ...
    'p99993', log(v), ...
    'p99994', log(v)-2);

resolved = hgf_config;
resolved.priormus(resolved.priormus==99991) = payload.placeholders.p99991;
resolved.priorsas(resolved.priorsas==99991) = payload.placeholders.p99991;
resolved.priormus(resolved.priormus==99992) = payload.placeholders.p99992;
resolved.priorsas(resolved.priorsas==99992) = payload.placeholders.p99992;
resolved.priormus(resolved.priormus==99993) = payload.placeholders.p99993;
resolved.priorsas(resolved.priorsas==99993) = payload.placeholders.p99993;
resolved.priormus(resolved.priormus==-99993) = -payload.placeholders.p99993;
resolved.priorsas(resolved.priorsas==-99993) = -payload.placeholders.p99993;
resolved.priormus(resolved.priormus==99994) = payload.placeholders.p99994;
resolved.priorsas(resolved.priorsas==99994) = payload.placeholders.p99994;
payload.hgf_resolved_priormus = resolved.priormus;
payload.hgf_resolved_priorsas = resolved.priorsas;

r = struct;
r.u = [0; 1; NaN; 1];
r.y = [1; NaN; 0; 1];
payload.masks.ignored = find(isnan(r.u(:,1)))';
payload.masks.irregular = unique([find(isnan(r.u(:,1))); find(isnan(r.y(:,1)))])';

r_regular = struct;
r_regular.u = [0.1; 0.2; 0.3];
r_regular.c_prc = struct('irregular_intervals', false);
payload.time_axis_regular = hgf_time_axis(r_regular, 4)';

r_irregular = struct;
r_irregular.u = [0.1 0.5; 0.2 2.0; 0.3 1.5];
r_irregular.c_prc = struct('irregular_intervals', true);
payload.time_axis_irregular = hgf_time_axis(r_irregular, 4)';

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m2:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M2 MATLAB export: PASS\n');
end


function out = export_config(c, transp_fun)
out = struct;
out.model = c.model;
out.priormus = c.priormus;
out.priorsas = c.priorsas;

free_mask = c.priorsas;
free_mask(isnan(free_mask)) = 0;
out.free_indices = find(free_mask);
out.fixed_indices = find(c.priorsas == 0);
out.undefined_indices = find(isnan(c.priorsas));

sample = linspace(-1, 1, length(c.priormus));
if strcmp(c.model, 'unitsq_sgm')
    r = struct;
else
    r = struct;
    r.c_prc = c;
end
[native, named] = transp_fun(r, sample);
out.sample_transformed = sample;
out.sample_native = native;
out.sample_named = named;

if isfield(c, 'n_levels')
    out.n_levels = c.n_levels;
end
if isfield(c, 'irregular_intervals')
    out.irregular_intervals = c.irregular_intervals;
end
if isfield(c, 'predorpost')
    out.predorpost = c.predorpost;
end
end
