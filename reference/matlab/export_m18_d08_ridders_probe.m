function export_m18_d08_ridders_probe(output_path)
% Decompose the first D08 Ridders gradient divergence at optimizer row 3.
% Diagnostic only; no gate/seed/data/model/optimizer setting is changed.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(root,'external','hgf-toolbox')));
addpath(fullfile(root,'reference','matlab','m11_shims'));

x = load(fullfile(root,'external','hgf-toolbox','demo','example_usdchf.txt'));
native = [1.04 1 .0001 .1 0 0 1 -13 -2 1e4];
obs_native = .00002;
seed = 123456789;

s = simModel(x,'uhgf',native,'gaussian_obs',obs_native,seed);
pc = uhgf_config();
oc = gaussian_obs_config();
fit = fitModel(s.y,x,pc,oc,'quasinewton_optim_config');

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

source_row = 3;       % MATLAB row 3 == zero-based optimizer row 2.
component = 1;        % First free parameter; first gradient divergence.
point = fit.optim.iter.x(source_row,:)';
probe = workflow_ridders_component(obj,point,component,r,init,opt_idx);

payload.protocol = 'm18-d08-ridders-probe-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D08_fit';
payload.model = 'uhgf';
payload.observation = 'gaussian_obs';
payload.seed = seed;
payload.inputs = x;
payload.responses = s.y;
payload.free_full_indices_1based = opt_idx;
payload.source_trace_row_1based = source_row;
payload.component_free_index_1based = component;
payload.source_x = point;
payload.probe = probe;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D08 Ridders probe exported: row %d component %d\n', source_row, component);
end

function out = workflow_ridders_component(f,x,k,r,init,opt_idx)
init_h = 1;
div = 1.2;
min_steps = 10;
max_steps = 100;
tf = 2;
P = NaN(max_steps);
hvals = NaN(max_steps,1);
xplus = NaN(max_steps,1);
xminus = NaN(max_steps,1);
fplus = NaN(max_steps,1);
fminus = NaN(max_steps,1);
central = NaN(max_steps,1);
diagonal = NaN(max_steps,1);
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
out.x0 = x(k);
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
