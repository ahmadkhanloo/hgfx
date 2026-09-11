function export_m18_horizon(input_path, output_path)
% Replay shared input/parameter arrays through UNMODIFIED frozen MATLAB code.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(root, 'external', 'hgf-toolbox');
[status, sha] = system(sprintf('git -C "%s" rev-parse HEAD', hgf_root));
assert(status == 0 && strcmp(strtrim(sha), '2437f4dc241541072722a2695ddeca7b44d83dd3'));
addpath(genpath(hgf_root));
data = jsondecode(fileread(input_path));
payload.reference_commit = strtrim(sha);
payload.matlab_version = version;
payload.purpose = 'forward/validation diagnostic only';
payload.cases = cell(numel(data.cases), 1);
fields = {'mu','sa','muhat','sahat','v','w','da'};
for i = 1:numel(data.cases)
    if iscell(data.cases)
        c = data.cases{i};
    else
        c = data.cases(i);
    end
    r = struct('u', c.inputs(:), 'ign', []);
    r.c_prc = feval([c.model '_config']);
    out = struct('model', c.model, 'trials', c.trials, 'replicate', c.replicate, ...
                 'seed', c.seed, 'point', c.point);
    try
        [traj, ~] = feval(c.model, r, c.ptrans(:)', 'trans');
        out.status = 'valid';
        for k = 1:numel(fields)
            a = traj.(fields{k});
            packed.shape = size(a);
            packed.nan = isnan(a);
            packed.posinf = isinf(a) & a > 0;
            packed.neginf = isinf(a) & a < 0;
            a(~isfinite(a)) = 0;
            packed.values = a;
            out.trajectory.(fields{k}) = packed;
        end
    catch err
        out.status = 'rejected';
        out.error_id = err.identifier;
        out.error = err.message;
    end
    payload.cases{i} = out;
end
fid = fopen(output_path, 'w');
assert(fid ~= -1);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
end
