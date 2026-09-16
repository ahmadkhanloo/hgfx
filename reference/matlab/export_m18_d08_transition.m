function export_m18_d08_transition(output_path)
% Focused D08 optimizer transition evidence at the first exact x split.
% Diagnostic only; no acceptance threshold, seed, data, model or optimizer
% setting is changed.
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

% Endpoint diagnostic v2 established that zero-based row 2 is still exact and
% zero-based row 3 contains the first stored x divergence. MATLAB indexing:
source_row = 3;
target_row = 4;
trace = fit.optim.iter;
point = trace.x(source_row,:)';
source_val = trace.val(source_row);
target_x = trace.x(target_row,:)';
target_val = trace.val(target_row);
T = trace.invH(source_row).T;

gradoptions.min_steps = 10;
[grad, grad_err] = riddersgradient(obj,point,gradoptions);
grad_col = grad';
desc_raw = -T*grad_col;
slope = grad*desc_raw;
step_size_raw = sqrt(desc_raw'*desc_raw);

copt = quasinewton_optim_config;
desc_limited = desc_raw;
if step_size_raw > copt.maxStep
    desc_limited = desc_raw*copt.maxStep/sqrt(desc_raw'*desc_raw);
end
step_size_limited = sqrt(desc_limited'*desc_limited);

candidate_template = struct('j',0,'t',NaN,'x',[],'val',NaN,'dval',NaN, ...
    'rhs',NaN,'finite',false,'armijo_accept',false);
candidates = repmat(candidate_template,copt.maxRegu+1,1);
accepted_j = NaN;
accepted_x = NaN(size(point));
accepted_val = NaN;
for j = 0:copt.maxRegu
    t = 0.5^j;
    candidate_x = point+t.*desc_limited;
    candidate_val = obj(candidate_x);
    finite = ~isinf(candidate_val);
    if finite
        dval = candidate_val-source_val;
    else
        dval = NaN;
    end
    rhs = 1e-4*t*slope;
    armijo_accept = finite && dval < rhs;
    candidates(j+1).j = j;
    candidates(j+1).t = t;
    candidates(j+1).x = candidate_x;
    candidates(j+1).val = candidate_val;
    candidates(j+1).dval = dval;
    candidates(j+1).rhs = rhs;
    candidates(j+1).finite = finite;
    candidates(j+1).armijo_accept = armijo_accept;
    if isnan(accepted_j) && armijo_accept
        accepted_j = j;
        accepted_x = candidate_x;
        accepted_val = candidate_val;
    end
end

payload.protocol = 'm18-d08-transition-diagnostic-1';
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
payload.target_trace_row_1based = target_row;
payload.source.x = point;
payload.source.val = source_val;
payload.source.invH = T;
payload.source.gradient = grad;
payload.source.gradient_error = grad_err;
payload.transition.descvec_raw = desc_raw;
payload.transition.slope = slope;
payload.transition.step_size_raw = step_size_raw;
payload.transition.descvec_limited = desc_limited;
payload.transition.step_size_limited = step_size_limited;
payload.transition.max_step = copt.maxStep;
payload.transition.max_regu = copt.maxRegu;
payload.transition.candidates = candidates;
payload.transition.accepted_j = accepted_j;
payload.transition.accepted_x = accepted_x;
payload.transition.accepted_val = accepted_val;
payload.target.x = target_x;
payload.target.val = target_val;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D08 transition diagnostic exported: source row %d -> target row %d\n', source_row, target_row);
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
