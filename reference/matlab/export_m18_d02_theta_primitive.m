function export_m18_d02_theta_primitive(output_plus_path, output_minus_path)
% Diagnostic-only D02 top-level theta/predicted-precision primitive probe.
% Targets the current parameter-2 Ridders argmax samples from run 34783447282.
% No acceptance threshold, seed, dataset, start point, optimizer, or model changes.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

u = load(fullfile(root,'external','hgf-toolbox','demo','example_binary_input.txt'));
seed = 123456789;
native = [NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3];

sim = simModel(u,'ehgf_binary',native,'unitsq_sgm',5,seed);
pc = ehgf_binary_config;
oc = unitsq_sgm_config;
oc.logzesa = .5;
oc = align_priors(oc);
fit = fitModel(sim.y,u,pc,oc,'quasinewton_optim_config');

r.u = fit.u;
r.y = fit.y;
r.irr = fit.irr;
r.ign = fit.ign;
r.c_prc = fit.c_prc;
r.c_obs = fit.c_obs;

init = fit.optim.init;
opt_mask = [r.c_prc.priorsas, r.c_obs.priorsas];
opt_mask(isnan(opt_mask)) = 0;
opt_idx = find(opt_mask);
n_prcpars = length(r.c_prc.priormus);
n_obspars = length(r.c_obs.priormus);

trace = fit.optim.iter;
finite_rows = find(all(isfinite(trace.x),2) & isfinite(trace.val));
x0 = trace.x(finite_rows(1),:)';

plus_payload = build_payload( ...
    r, u, sim.y, init, opt_idx, n_prcpars, n_obspars, x0, ...
    1/(1.2^7), +1, 'parameter_2_ridders_plus_step_8');
minus_payload = build_payload( ...
    r, u, sim.y, init, opt_idx, n_prcpars, n_obspars, x0, ...
    1/(1.2^8), -1, 'parameter_2_ridders_minus_step_9');

write_payload(output_plus_path, plus_payload);
write_payload(output_minus_path, minus_payload);

fprintf('M18 D02 theta primitive probes: plus_logtheta=%.17g minus_logtheta=%.17g\n', ...
    plus_payload.primitives.logtheta, minus_payload.primitives.logtheta);
end

function payload = build_payload(r, u, responses, init, opt_idx, n_prcpars, n_obspars, x0, h, direction, sample_name)
sample_free = x0;
sample_free(2) = x0(2) + direction*h;

full = init;
full(opt_idx) = sample_free;
ptrans_prc = full(1:n_prcpars);

[traj,infStates] = r.c_prc.prc_fun(r,ptrans_prc,'trans');

l = r.c_prc.n_levels;
logsa0_last = ptrans_prc(2*l);
sa0_last = exp(logsa0_last);
pi_prev_last = 1/sa0_last;
logtheta = ptrans_prc(5*l-1);
theta = exp(logtheta);
if isfield(r.c_prc,'irregular_intervals') && r.c_prc.irregular_intervals
    t_first = r.u(1,end);
else
    t_first = 1;
end
reciprocal_pi_prev = 1/pi_prev_last;
t_theta = t_first * theta;
inner = reciprocal_pi_prev + t_theta;
pihat_first = 1/inner;
sahat_first = 1/pihat_first;
traj_sahat_first = traj.sahat(1,l);
inf_sahat_first = infStates(1,l,2);

payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.protocol = 'm18-d02-theta-primitive-1';
payload.case_id = 'D02_fit';
payload.sample = sample_name;
payload.inputs = u;
payload.responses = responses;
payload.obs_prior_variance = .5;
payload.sample_free = sample_free;
payload.full_transformed = full;
payload.n_perceptual = n_prcpars;
payload.n_observation = n_obspars;
payload.n_levels = l;
payload.primitives.logsa0_last = logsa0_last;
payload.primitives.sa0_last = sa0_last;
payload.primitives.pi_prev_last = pi_prev_last;
payload.primitives.logtheta = logtheta;
payload.primitives.theta = theta;
payload.primitives.t_first = t_first;
payload.primitives.reciprocal_pi_prev = reciprocal_pi_prev;
payload.primitives.t_theta = t_theta;
payload.primitives.inner = inner;
payload.primitives.pihat_first = pihat_first;
payload.primitives.sahat_first = sahat_first;
payload.primitives.traj_sahat_first = traj_sahat_first;
payload.primitives.inf_sahat_first = inf_sahat_first;
end

function write_payload(output_path, payload)
folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w');
assert(fid>=0);
cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
end
