function export_m18_d02_matlab_self_sensitivity(output_path)
% Frozen diagnostic-only MATLAB start-point self-sensitivity probe for D02.
% See docs/validation/M18_D02_MATLAB_SELF_SENSITIVITY.md.
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
copt = quasinewton_optim_config;

free_init = init(opt_idx)';
baseline = quasinewton_optim(obj,free_init,copt);

nfree = length(free_init);
variants = cell(2*nfree,1);
q = 0;
for k = 1:nfree
    local_spacing = eps(free_init(k));
    for direction = [-1, 1]
        q = q + 1;
        start = free_init;
        start(k) = free_init(k) + direction*local_spacing;
        result = quasinewton_optim(obj,start,copt);
        item.label = sprintf('free_%d_%s_eps',k,ternary(direction<0,'minus','plus'));
        item.component_free_index_1based = k;
        item.component_full_index_1based = opt_idx(k);
        item.direction = direction;
        item.requested_spacing = local_spacing;
        item.actual_delta = start(k)-free_init(k);
        item.start = start;
        item.argMin = result.argMin;
        item.valMin = result.valMin;
        item.T = result.T;
        item.iter_x = result.iter.x;
        item.iter_val = result.iter.val;
        item.iter_rst = result.iter.rst;
        variants{q} = item;
    end
end
variants = vertcat(variants{:});

payload.protocol = 'm18-d02-matlab-self-sensitivity-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D02_fit';
payload.seed = seed;
payload.obs_prior_variance = .5;
payload.inputs = u;
payload.responses = s.y;
payload.free_full_indices_1based = opt_idx;
payload.official_full_init = fit.optim.init;
payload.official_full_final = fit.optim.final;
payload.official_free_final = fit.optim.final(opt_idx)';
payload.free_init = free_init;
payload.baseline.argMin = baseline.argMin;
payload.baseline.valMin = baseline.valMin;
payload.baseline.T = baseline.T;
payload.baseline.iter_x = baseline.iter.x;
payload.baseline.iter_val = baseline.iter.val;
payload.baseline.iter_rst = baseline.iter.rst;
payload.variants = variants;

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D02 MATLAB self-sensitivity exported: %d one-spacing starts\n',numel(variants));
end

function out = ternary(cond,a,b)
if cond
    out = a;
else
    out = b;
end
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
if isnan(logLl)
    negLogJoint = realmax;
    return;
end
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
