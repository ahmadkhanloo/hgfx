function export_m18_d08_holdout_optimizer_probe(output_path)
% Diagnostic-only probe for the failed D08 prospective holdout seed 314159265.
% Frozen by docs/validation/M18_D08_HOLDOUT_OPTIMIZER_DIAGNOSTIC.md.
% This does not change any acceptance gate, seed, tolerance, data, model, start, or optimizer.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

x = load(fullfile(root,'external','hgf-toolbox','demo','example_usdchf.txt'));
seed = 314159265;
native = [1.04 1 .0001 .1 0 0 1 -13 -2 1e4];
obs_native = .00002;

sim = simModel(x,'uhgf',native,'gaussian_obs',obs_native,seed);
pc = uhgf_config();
oc = gaussian_obs_config();
fit = fitModel(sim.y,x,pc,oc,'quasinewton_optim_config');

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
requested_rows = 38:44;
valid = requested_rows(requested_rows <= size(trace.x,1));
finite_mask = all(isfinite(trace.x(valid,:)),2) & isfinite(trace.val(valid));
rows = valid(finite_mask);
assert(~isempty(rows),'No requested finite optimizer rows available.');

probe.rows = rows;
probe.x = trace.x(rows,:);
probe.val = trace.val(rows);
probe.grad = NaN(numel(rows),size(trace.x,2));
probe.grad_err = NaN(numel(rows),size(trace.x,2));
probe.invH = cell(numel(rows),1);
gradoptions.min_steps = 10;

for q = 1:numel(rows)
    row = rows(q);
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
payload.protocol = 'm18-d08-holdout-optimizer-probe-1';
payload.case_id = 'D08_fit';
payload.seed = seed;
payload.inputs = x;
payload.responses = sim.y;
payload.native = native;
payload.obs_native = obs_native;
payload.final = fit.optim.final;
payload.negLj = fit.optim.negLj;
payload.trace.full_x = trace.x;
payload.trace.full_val = trace.val;
payload.trace.full_rst = trace.rst;
payload.trace.window = probe;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));

fprintf('M18 D08 failed-holdout optimizer probe: seed=%d rows=%s\n',seed,mat2str(rows));
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
