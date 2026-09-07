function export_m6_uhgf_forward_parity(output_path)
%EXPORT_M6_UHGF_FORWARD_PARITY Export frozen HGF v8.2.0 uHGF trajectories and diagnostics.

repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root = fullfile(repo_root, 'external', 'hgf-toolbox');
addpath(genpath(hgf_root));

payload = struct;
payload.metadata.schema_version = 'm6-1';
payload.metadata.reference_toolbox = 'HGF Toolbox';
payload.metadata.reference_version = '8.2.0';
payload.metadata.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.metadata.matlab_version = version;
payload.metadata.numeric_mode = 'CPU float64';
payload.metadata.rng = 'deterministic/no RNG';
payload.metadata.optimizer = 'none';
payload.metadata.response_model = 'none';
payload.metadata.binary_forward = which('hgf_binary_unified');
payload.metadata.continuous_forward = which('hgf_unified');
payload.metadata.volatility_update = which('hgf_volatility_update');
payload.metadata.lambert_w0 = which('lambert_w0');

nominal = {0.25, 2.0, 0.7, 3.0, 0.2, 0.1, -2.0, 2.5, 3.2, 0.4, 0.35, 1.3};
payload.diagnostics.nominal = uhgf_details(nominal);

extreme = {0.2, 1e-4, 1.0, 0.5, 0.3, 0.1, -1.0, 1.5, 2.0, 0.4, 0.35, 1.0};
payload.diagnostics.logspace_fallback = uhgf_details(extreme);

binary_u = [0 1 1 0 1 0 1 1 0 0 1 1 1 0 1 0 0 1 1 0 1 0 1 1]';
binary_p = [NaN 0 1 NaN log(0.1) 0 NaN 0 0 0 0 NaN -3 2];
payload.trajectories.binary_regular = run_binary(binary_u, binary_p, false);

binary_dt = [0.5 1.0 1.5 0.8 1.2 0.7 1.1 0.9 1.3 1.0 0.6 1.4 1.0 0.75 1.25 0.8 1.1 0.9 1.2 0.7 1.3 0.85 1.15 0.95]';
binary_irr = [binary_u, binary_dt];
binary_irr(6,1) = NaN;
payload.trajectories.binary_irregular_ignored = run_binary(binary_irr, binary_p, true);

continuous_u = [0.20 0.25 0.18 0.30 0.22 0.27 0.24 0.31 0.29 0.20 0.19 0.23 0.26 0.28 0.30 0.25 0.21 0.18 0.20 0.24 0.27 0.29 0.26 0.22]';
continuous_p = [0.2 1.0 log(0.05) log(0.1) 0 0 0 -4 -6 log(100)];
payload.trajectories.continuous_regular = run_continuous(continuous_u, continuous_p, false);

continuous_dt = linspace(0.6, 1.4, length(continuous_u))';
continuous_irr = [continuous_u, continuous_dt];
continuous_irr(7,1) = NaN;
payload.trajectories.continuous_irregular_ignored = run_continuous(continuous_irr, continuous_p, true);

output_dir = fileparts(output_path);
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
fid = fopen(output_path, 'w');
if fid == -1
    error('hgfx:m6:openFailed', 'Could not open %s', output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, 'PrettyPrint', true));
fprintf('HGFX M6 MATLAB uHGF forward export: PASS\n');
end

function out = uhgf_details(args)
muhat_j = args{1};
pihat_j = args{2};
ka_jm1 = args{3};
da_jm1 = args{5};
om_jm1 = args{7};
pi_prev_jm1 = args{8};
pi_jm1 = args{9};
mu_jm1 = args{10};
muhat_jm1 = args{11};
t_k = args{12};

v_jm1 = t_k * exp(ka_jm1 * muhat_j + om_jm1);
if isinf(v_jm1)
    w_jm1 = 1;
else
    w_jm1 = 1 / (1 + 1/(pi_prev_jm1 * v_jm1));
end

pi1 = pihat_j + 1/2 * ka_jm1^2 * w_jm1 * (1 - w_jm1);
mu1 = muhat_j + 1/2 * 1/pi1 * ka_jm1 * w_jm1 * da_jm1;

al_aux = 1/pi_prev_jm1;
be_aux = 1/pi_jm1 + (mu_jm1 - muhat_jm1)^2;
gamma_c = log(t_k) + ka_jm1 * muhat_j + om_jm1;
pihat_y = pihat_j / ka_jm1^2;
log_W_arg = log(be_aux) - log(2 * pihat_y) + 0.5/pihat_y - gamma_c;
max_log = log(realmax('double'));
W_arg = exp(min(log_W_arg, max_log));
v_W = lambert_w0(W_arg);
y_star = gamma_c + v_W - 0.5/pihat_y;
x_star = (y_star - log(t_k) - om_jm1) / ka_jm1;

s2 = t_k * exp(ka_jm1 * x_star + om_jm1);
if isinf(s2)
    w2 = 1;
    da2 = -1;
else
    w2 = 1 / (1 + al_aux / s2);
    da2 = be_aux / (al_aux + s2) - 1;
end

pi2_raw = pihat_j + 1/2 * ka_jm1^2 * w2 * (w2 + (2*w2 - 1) * da2);
pi2 = pi2_raw;
precision_fallback = pi2 <= 0;
if precision_fallback
    pi2 = pihat_j + 1/2 * ka_jm1^2 * w2 * (1 - w2);
end
mu2 = x_star + (1/2 * ka_jm1 * w2 * da2 - pihat_j * (x_star - muhat_j)) / pi2;

nonfinite_fallback = ~isfinite(pi2) || ~isfinite(mu2);
if nonfinite_fallback
    pi2 = pi1;
    mu2 = mu1;
end

ey1 = t_k * exp(ka_jm1 * mu1 + om_jm1);
I1 = -1/2 * log(al_aux + ey1) - 1/2 * be_aux / (al_aux + ey1) ...
     - 1/2 * pihat_j * (mu1 - muhat_j)^2;
ey2 = t_k * exp(ka_jm1 * mu2 + om_jm1);
I2 = -1/2 * log(al_aux + ey2) - 1/2 * be_aux / (al_aux + ey2) ...
     - 1/2 * pihat_j * (mu2 - muhat_j)^2;
b = 1 / (1 + exp(I1 - I2));
mu_final = (1 - b) * mu1 + b * mu2;
sig2 = (1 - b) / pi1 + b / pi2 + b * (1 - b) * (mu1 - mu2)^2;
pi_final = 1 / sig2;

[public_pi, public_mu, public_v, public_w] = hgf_volatility_update(args{:}, 'uhgf');

out = struct;
out.v = v_jm1;
out.w = w_jm1;
out.pi1 = pi1;
out.mu1 = mu1;
out.al_aux = al_aux;
out.be_aux = be_aux;
out.gamma_c = gamma_c;
out.pihat_y = pihat_y;
out.log_w_arg = log_W_arg;
out.max_log = max_log;
out.w_arg = W_arg;
out.v_w = v_W;
out.y_star = y_star;
out.x_star = x_star;
out.s2 = s2;
out.w2 = w2;
out.da2 = da2;
out.pi2_raw = pi2_raw;
out.precision_fallback = precision_fallback;
out.pi2 = pi2;
out.mu2 = mu2;
out.nonfinite_fallback = nonfinite_fallback;
out.ey1 = ey1;
out.i1 = I1;
out.ey2 = ey2;
out.i2 = I2;
out.blend = b;
out.final_mu = mu_final;
out.final_sig2 = sig2;
out.final_pi = pi_final;
out.public_output = [public_pi, public_mu, public_v, public_w];
end

function out = run_binary(inputs, ptrans, irregular_intervals)
r = struct;
r.u = inputs;
r.ign = find(isnan(r.u(:,1)))';
r.c_prc = uhgf_binary_config;
r.c_prc.irregular_intervals = irregular_intervals;
r.c_prc.update_type = 'uhgf';
[traj, infStates] = hgf_binary_unified(r, ptrans, 'trans');
out = struct;
out.model = 'uhgf_binary';
out.inputs = inputs;
out.ptrans = ptrans;
out.irregular_intervals = irregular_intervals;
out.ignored_matlab_indices = r.ign;
out.traj = traj;
out.inf_states = infStates;
end

function out = run_continuous(inputs, ptrans, irregular_intervals)
r = struct;
r.u = inputs;
r.ign = find(isnan(r.u(:,1)))';
r.c_prc = uhgf_config;
r.c_prc.irregular_intervals = irregular_intervals;
r.c_prc.update_type = 'uhgf';
[traj, infStates] = hgf_unified(r, ptrans, 'trans');
out = struct;
out.model = 'uhgf';
out.inputs = inputs;
out.ptrans = ptrans;
out.irregular_intervals = irregular_intervals;
out.ignored_matlab_indices = r.ign;
out.traj = traj;
out.inf_states = infStates;
end
