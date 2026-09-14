function export_m18_d02_optimizer_source_probe(output_path)
% Frozen diagnostic-only Ridders probe at the D02 optimizer source state.
% See docs/validation/M18_D02_OPTIMIZER_SOURCE_PROBE.md.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

u = load(fullfile(root,'external','hgf-toolbox','demo','example_binary_input.txt'));
seed = 123456789;
native = [NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3];
s = simModel(u,'ehgf_binary',native,'unitsq_sgm',5,seed);
pc = ehgf_binary_config;
oc = unitsq_sgm_config;
oc.logzesa = .5;
oc = align_priors(oc);
fit = fitModel(s.y,u,pc,oc,'quasinewton_optim_config');

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

source_row = 7; % one-based MATLAB iter row; frozen before execution
point = fit.optim.iter.x(source_row,:)';
component_count = length(point);
probe = cell(component_count,1);
for k = 1:component_count
    probe{k} = workflow_ridders_component(obj,point,k,r,init,opt_idx);
end
probe = vertcat(probe{:});

gradoptions.min_steps = 10;
[grad, grad_err] = riddersgradient(obj,point,gradoptions);

payload.protocol = 'm18-d02-optimizer-source-probe-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D02_fit';
payload.model = 'ehgf_binary';
payload.observation = 'unitsq_sgm';
payload.seed = seed;
payload.obs_prior_variance = .5;
payload.inputs = u;
payload.responses = s.y;
payload.free_full_indices_1based = opt_idx;
payload.source_trace_row_1based = source_row;
payload.source_x = point;
payload.source_val = fit.optim.iter.val(source_row);
payload.source_invH = fit.optim.iter.invH(source_row).T;
payload.selected_gradient = grad;
payload.selected_gradient_error = grad_err;
payload.probes = probe;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D02 optimizer source probe exported: row %d components %d\n', source_row, component_count);
end

function out = workflow_ridders_component(f,x,k,r,init,opt_idx)
init_h = 1;
div = 1.2;
min_steps = 10;
max_steps = 100;
tf = 2;
P = NaN(max_steps);
hvals = NaN(max_steps,1);
fplus = NaN(max_steps,1);
fminus = NaN(max_steps,1);
central = NaN(max_steps,1);
diagonal = NaN(max_steps,1);
xplus = NaN(max_steps,1);
xminus = NaN(max_steps,1);
plus_decomp = repmat(struct('log_likelihood',NaN,'perceptual_prior',NaN, ...
    'observation_prior',NaN,'neg_log_joint',NaN),max_steps,1);
minus_decomp = plus_decomp;

h = init_h;
df = NaN;
err = realmax;
stop_step = max_steps;
for i = 1:max_steps
    if i > 1
        h = h/div;
    end
    xp = x;
    xm = x;
    xp(k) = x(k)+h;
    xm(k) = x(k)-h;
    fp = f(xp);
    fm = f(xm);
    P(i,1) = (fp-fm)/(2*h);
    hvals(i) = h;
    xplus(i) = xp(k);
    xminus(i) = xm(k);
    fplus(i) = fp;
    fminus(i) = fm;
    central(i) = P(i,1);
    plus_decomp(i) = workflow_decompose_free(r,init,opt_idx,xp);
    minus_decomp(i) = workflow_decompose_free(r,init,opt_idx,xm);
    if i > 1
        divsq = div^2;
        t = divsq;
        for j = 2:i
            P(i,j) = (t*P(i,j-1)-P(i-1,j-1))/(t-1);
            t = t*divsq;
            currerr = max(abs(P(i,j)-P(i,j-1)),abs(P(i,j)-P(i-1,j-1)));
            if currerr < err
                err = currerr;
                df = P(i,j);
            end
        end
    end
    diagonal(i) = P(i,i);
    if i > min_steps && abs(P(i,i)-P(i-1,i-1)) > tf*err
        stop_step = i;
        break;
    end
end
keep = 1:stop_step;
out.component_free_index_1based = k;
out.h = hvals(keep);
out.x_plus = xplus(keep);
out.x_minus = xminus(keep);
out.f_plus = fplus(keep);
out.f_minus = fminus(keep);
out.central_difference = central(keep);
out.diagonal = diagonal(keep);
out.selected_derivative = df;
out.selected_error = err;
out.stop_step = stop_step;
out.plus_decomposition = plus_decomp(keep);
out.minus_decomposition = minus_decomp(keep);
end

function d = workflow_decompose_free(r,init,opt_idx,free_arg)
full = init;
full(opt_idx) = free_arg;
n_prcpars = length(r.c_prc.priormus);
n_obspars = length(r.c_obs.priormus);
ptrans_prc = full(1:n_prcpars);
ptrans_obs = full(n_prcpars+1:n_prcpars+n_obspars);
[~,infStates] = r.c_prc.prc_fun(r,ptrans_prc,'trans');
try
    [trialLogLls,~,~,~] = r.c_obs.obs_fun(r,infStates,ptrans_obs);
catch
    trialLogLls = r.c_obs.obs_fun(r,infStates,ptrans_obs);
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
d.log_likelihood = logLl;
d.perceptual_prior = logPrcPrior;
d.observation_prior = logObsPrior;
d.neg_log_joint = -(logLl+logPrcPrior+logObsPrior);
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
