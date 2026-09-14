function export_m18_d08_prior_terms(output_path)
% Freeze the exact perceptual Gaussian-prior arithmetic at the first D08
% Ridders objective divergence. Diagnostic only.
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

source_row = 3; % zero-based row 2
component = 1;  % first free parameter
point = fit.optim.iter.x(source_row,:)';
plus = point;
plus(component) = plus(component)+1;
full = init;
full(opt_idx) = plus;
n_prcpars = length(r.c_prc.priormus);
ptrans_prc = full(1:n_prcpars);

prc_idx = r.c_prc.priorsas;
prc_idx(isnan(prc_idx)) = 0;
prc_idx = find(prc_idx);
selected_parameters = ptrans_prc(prc_idx);
selected_means = r.c_prc.priormus(prc_idx);
selected_variances = r.c_prc.priorsas(prc_idx);
normalization_terms = -1/2.*log(8*atan(1).*selected_variances);
quadratic_terms = -1/2.*(selected_parameters-selected_means).^2./selected_variances;
prior_terms = normalization_terms + quadratic_terms;
prior_total = sum(prior_terms);

payload.protocol = 'm18-d08-prior-terms-1';
payload.reference_commit = '2437f4dc241541072722a2695ddeca7b44d83dd3';
payload.numeric_encoding = 'ieee-strings-v1';
payload.matlab_version = version;
payload.case_id = 'D08_fit';
payload.seed = seed;
payload.inputs = x;
payload.responses = s.y;
payload.source_trace_row_1based = source_row;
payload.component_free_index_1based = component;
payload.free_full_indices_1based = opt_idx;
payload.source_x = point;
payload.sample_free = plus;
payload.prior.indices_1based = prc_idx;
payload.prior.parameters = selected_parameters;
payload.prior.means = selected_means;
payload.prior.variances = selected_variances;
payload.prior.normalization_terms = normalization_terms;
payload.prior.quadratic_terms = quadratic_terms;
payload.prior.terms = prior_terms;
payload.prior.total = prior_total;
payload.prior.constant_8atan1 = 8*atan(1);

folder = fileparts(output_path);
if ~exist(folder,'dir'); mkdir(folder); end
fid = fopen(output_path,'w'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(hgfx_json_ieee(payload),'PrettyPrint',true));
fprintf('M18 D08 prior-term diagnostic exported.\n');
end
