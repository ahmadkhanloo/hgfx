function export_m18_d02_objective_decomposition(output_path)
% Diagnostic-only objective decomposition for the exact D02 Ridders samples.
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

parts_fun = @(free_arg) restrict_parts(r,r.c_prc.prc_fun,r.c_obs.obs_fun, ...
    init,opt_idx,free_arg,n_prcpars,n_obspars);

payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.protocol = 'm18-d02-objective-decomposition-1';
payload.case_id = 'D02_fit';
payload.inputs = u;
payload.responses = sim.y;
payload.obs_prior_variance = .5;
payload.initial_free = x0;
payload.samples = collect_ridders_samples(parts_fun,x0);

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w');
assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));

fprintf('M18 D02 objective decomposition: parameters=%d\n',numel(x0));
end

function parts = restrict_parts(r,prc_fun,obs_fun,arg,free_idx,free_arg,n_prcpars,n_obspars)
arg(free_idx) = free_arg;
parts = objective_parts(r,prc_fun,obs_fun, ...
    arg(1:n_prcpars),arg(n_prcpars+1:n_prcpars+n_obspars));
end

function parts = objective_parts(r,prc_fun,obs_fun,ptrans_prc,ptrans_obs)
[~,infStates] = prc_fun(r,ptrans_prc,'trans');
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

parts.neg_log_joint = -(logLl+logPrcPrior+logObsPrior);
parts.log_likelihood = logLl;
parts.trial_log_likelihoods = trialLogLls(:)';
parts.perceptual_prior_total = logPrcPrior;
parts.perceptual_prior_terms = logPrcPriors(:)';
parts.observation_prior_total = logObsPrior;
parts.observation_prior_terms = logObsPriors(:)';
end

function samples = collect_ridders_samples(parts_fun,x)
init_h = 1;
div = 1.2;
min_steps = 10;
max_steps = 100;
tf = 2;
n = length(x);

template = struct('parameter_index_1based',0,'x0',NaN,'h',[], ...
    'x_plus',[],'x_minus',[],'plus',struct(),'minus',struct(), ...
    'central_difference',[],'diagonal',[],'selected_derivative',NaN, ...
    'selected_error',NaN,'stop_step',0);
samples = repmat(template,1,n);

for k = 1:n
    xi = x(k);
    P = NaN(max_steps);
    hvals = NaN(max_steps,1);
    xplus = NaN(max_steps,1);
    xminus = NaN(max_steps,1);
    plus = cell(max_steps,1);
    minus = cell(max_steps,1);
    central = NaN(max_steps,1);
    diagonal = NaN(max_steps,1);
    h = init_h;
    df = NaN;
    err = realmax;
    stop_step = max_steps;

    for i = 1:max_steps
        if i > 1; h = h/div; end
        xp = x; xm = x;
        xp(k) = xi+h;
        xm(k) = xi-h;
        pp = parts_fun(xp);
        pm = parts_fun(xm);
        P(i,1) = (pp.neg_log_joint-pm.neg_log_joint)/(2*h);
        hvals(i) = h;
        xplus(i) = xp(k);
        xminus(i) = xm(k);
        plus{i} = pp;
        minus{i} = pm;
        central(i) = P(i,1);

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
    samples(k).parameter_index_1based = k;
    samples(k).x0 = xi;
    samples(k).h = hvals(keep);
    samples(k).x_plus = xplus(keep);
    samples(k).x_minus = xminus(keep);
    samples(k).plus = pack_parts(plus(keep));
    samples(k).minus = pack_parts(minus(keep));
    samples(k).central_difference = central(keep);
    samples(k).diagonal = diagonal(keep);
    samples(k).selected_derivative = df;
    samples(k).selected_error = err;
    samples(k).stop_step = stop_step;
end
end

function packed = pack_parts(items)
n = numel(items);
packed.neg_log_joint = NaN(n,1);
packed.log_likelihood = NaN(n,1);
packed.perceptual_prior_total = NaN(n,1);
packed.observation_prior_total = NaN(n,1);
packed.trial_log_likelihoods = NaN(n,numel(items{1}.trial_log_likelihoods));
packed.perceptual_prior_terms = NaN(n,numel(items{1}.perceptual_prior_terms));
packed.observation_prior_terms = NaN(n,numel(items{1}.observation_prior_terms));
for i = 1:n
    p = items{i};
    packed.neg_log_joint(i) = p.neg_log_joint;
    packed.log_likelihood(i) = p.log_likelihood;
    packed.perceptual_prior_total(i) = p.perceptual_prior_total;
    packed.observation_prior_total(i) = p.observation_prior_total;
    packed.trial_log_likelihoods(i,:) = p.trial_log_likelihoods;
    packed.perceptual_prior_terms(i,:) = p.perceptual_prior_terms;
    packed.observation_prior_terms(i,:) = p.observation_prior_terms;
end
end
