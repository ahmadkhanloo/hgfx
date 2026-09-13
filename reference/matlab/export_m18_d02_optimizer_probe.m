function export_m18_d02_optimizer_probe(output_path)
% Diagnostic-only probe for the first D02 optimizer divergence.
% This does not change any M18 gate, threshold, seed, dataset or model choice.
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
nlj = @(p) workflow_nlj(r,r.c_prc.prc_fun,r.c_obs.obs_fun, ...
    p(1:n_prcpars),p(n_prcpars+1:n_prcpars+n_obspars));
obj = @(p_opt) workflow_restrict(nlj,init,opt_idx,p_opt);

trace = fit.optim.iter;
finite_rows = find(all(isfinite(trace.x),2) & isfinite(trace.val));
finite_rows = finite_rows(1:min(12,numel(finite_rows)));
n_free = size(trace.x,2);

probe.rows = finite_rows;
probe.x = trace.x(finite_rows,:);
probe.val = trace.val(finite_rows);
probe.grad = NaN(numel(finite_rows),n_free);
probe.grad_err = NaN(numel(finite_rows),n_free);
probe.invH = cell(numel(finite_rows),1);
gradoptions.min_steps = 10;

for q = 1:numel(finite_rows)
    row = finite_rows(q);
    point = trace.x(row,:)';
    [g,e] = riddersgradient(obj,point,gradoptions);
    probe.grad(q,:) = g;
    probe.grad_err(q,:) = e;
    if row <= numel(trace.invH) && isfield(trace.invH(row),'T') && ~isempty(trace.invH(row).T)
        probe.invH{q} = trace.invH(row).T;
    else
        probe.invH{q} = [];
    end
end

payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.protocol = 'm18-d02-optimizer-probe-1';
payload.case_id = 'D02_fit';
payload.inputs = u;
payload.responses = sim.y;
payload.obs_prior_variance = .5;
payload.final = fit.optim.final;
payload.negLj = fit.optim.negLj;
payload.trace = probe;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w');
assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));

fprintf('M18 D02 optimizer probe: rows=%s\n',mat2str(finite_rows'));
end

function val = workflow_restrict(f,arg,free_idx,free_arg)
arg(free_idx) = free_arg;
val = f(arg);
end

function negLogJoint = workflow_nlj(r,prc_fun,obs_fun,ptrans_prc,ptrans_obs)
try
    [~,infStates] = prc_fun(r,ptrans_prc,'trans');
catch
    negLogJoint = realmax;
    return;
end
try
    [trialLogLls,~,~,~] = obs_fun(r,infStates,ptrans_obs);
catch
    trialLogLls = obs_fun(r,infStates,ptrans_obs);
end
trialLogLls(r.irr) = [];
logLl = sum(trialLogLls);

prc_idx = r.c_prc.priorsas;
prc_idx(isnan(prc_idx)) = 0;
prc_idx = find(prc_idx);
logPrcPriors = -1/2.*log(8*atan(1).*r.c_prc.priorsas(prc_idx)) ...
    - 1/2.*(ptrans_prc(prc_idx)-r.c_prc.priormus(prc_idx)).^2 ...
    ./r.c_prc.priorsas(prc_idx);
logPrcPrior = sum(logPrcPriors);

obs_idx = r.c_obs.priorsas;
obs_idx(isnan(obs_idx)) = 0;
obs_idx = find(obs_idx);
logObsPriors = -1/2.*log(8*atan(1).*r.c_obs.priorsas(obs_idx)) ...
    - 1/2.*(ptrans_obs(obs_idx)-r.c_obs.priormus(obs_idx)).^2 ...
    ./r.c_obs.priorsas(obs_idx);
logObsPrior = sum(logObsPriors);

negLogJoint = -(logLl+logPrcPrior+logObsPrior);
end
