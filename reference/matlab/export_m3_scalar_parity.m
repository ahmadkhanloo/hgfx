function export_m3_scalar_parity(output_path)
%EXPORT_M3_SCALAR_PARITY Export frozen HGF v8.2.0 utility results for HGFX M3.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

payload = struct;

payload.logit.x = [0.1 0.2 0.5 0.8 0.9];
payload.logit.upper = 1;
payload.logit.y = tapas_logit(payload.logit.x, payload.logit.upper);

payload.logit_upper2.x = [0.1 0.5 1.0 1.5 1.9];
payload.logit_upper2.upper = 2;
payload.logit_upper2.y = tapas_logit(payload.logit_upper2.x, payload.logit_upper2.upper);

payload.sgm.x = [-12 -2 0 2 12];
payload.sgm.upper = 1;
payload.sgm.y = tapas_sgm(payload.sgm.x, payload.sgm.upper);

payload.sgm_upper2.x = [-4 -1 0 1 4];
payload.sgm_upper2.upper = 2;
payload.sgm_upper2.y = tapas_sgm(payload.sgm_upper2.x, payload.sgm_upper2.upper);

payload.boltzmann.x = [-2 0 1 3];
payload.boltzmann.beta = 0.7;
payload.boltzmann.y = boltzmann(payload.boltzmann.x, payload.boltzmann.beta);

payload.boltzmann_beta2.x = [-1 0.5 2];
payload.boltzmann_beta2.beta = 2;
payload.boltzmann_beta2.y = boltzmann(payload.boltzmann_beta2.x, payload.boltzmann_beta2.beta);

payload.lambert.x = [0 1e-12 9e-11 1e-10 1e-6 0.1 1 3 3.1 exp(1) 10 1e3 1e10];
payload.lambert.y = arrayfun(@lambert_w0, payload.lambert.x);

cov = [4 1 -2; 1 9 3; -2 3 16];
payload.cov2corr.input = cov;
payload.cov2corr.output = tapas_Cov2Corr(cov);

psd_in = [1 2 0; 2 1 0.5; 0 0.5 -0.2];
payload.nearest_psd.input = psd_in;
payload.nearest_psd.output = nearest_psd(psd_in);

opts = struct('init_h', 1, 'div', 1.2, 'min_steps', 5, 'max_steps', 100, 'tf', 2);
[d1, e1] = riddersdiff(@sin, 0.37, opts);
[d2, e2] = riddersdiff2(@exp, 0.4, opts);
payload.ridders.first.value = d1;
payload.ridders.first.error = e1;
payload.ridders.second.value = d2;
payload.ridders.second.error = e2;

cross_fun = @(v) v(1)^2 + 3*v(1)*v(2) + 2*v(2)^2;
[dc, ec] = riddersdiffcross(cross_fun, [0.4 -0.8], opts);
payload.ridders.cross.value = dc;
payload.ridders.cross.error = ec;

A = [4 1 -0.5; 1 3 0.25; -0.5 0.25 2];
b = [0.5; -1; 2];
x0 = [0.3; -0.7; 1.2];
quad = @(v) 0.5 .* v(:)' * A * v(:) + b' * v(:) + 0.7;
[g, ge] = riddersgradient(quad, x0, opts);
[h, he] = riddershessian(quad, x0, opts);
payload.ridders.quadratic.x = x0';
payload.ridders.quadratic.gradient = g(:)';
payload.ridders.quadratic.gradient_error = ge(:)';
payload.ridders.quadratic.hessian = h;
payload.ridders.quadratic.hessian_error = he;

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m3:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M3 MATLAB scalar export: PASS\n');
end
