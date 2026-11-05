function run_published_realdata_matlab()
% Physical MATLAB execution against pinned HGF Toolbox 8.2.0.
% Published source is older; this is NOT historical original-paper reproduction.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
toolbox = fullfile(root, 'external', 'hgf-toolbox');
addpath(toolbox);
addpath(fullfile(toolbox, 'core'));
addpath(fullfile(toolbox, 'perceptual'));
addpath(fullfile(toolbox, 'building_blocks'));
addpath(fullfile(toolbox, 'utilities'));

impl = which('hgf_ar1_binary_mab');
assert(contains(impl, 'hgf-toolbox'), 'MATLAB model is not from the pinned submodule');
fprintf('MATLAB_RELEASE=%s\n', version);
fprintf('MATLAB_HGF_IMPLEMENTATION=%s\n', impl);

folder = fullfile(root, 'published_pair_tmp');
cases = {'suthaharan_2021', 'reed_2020'};
p = [NaN, 0, 1, NaN, 0.1, 1, NaN, 0, 0.2, NaN, 0, 1, 1, 1, NaN, -2, -6];
for ci=1:numel(cases)
    label = cases{ci};
    x = readmatrix(fullfile(folder, [label '_input.txt']), 'FileType','text');
    assert(isequal(size(x),[80 2]), 'Blocked: source trial shape wrong');
    u = x(:,1);
    choices = x(:,2);
    assert(all(ismember(u(~isnan(u)),[0,1])), 'Blocked: outcome coding incompatible');
    assert(all(ismember(choices(~isnan(choices)),[1,2,3])), 'Blocked: choice coding incompatible');
    r = struct;
    r.u = [u, choices];
    r.y = choices;
    r.ign = find(isnan(u) | isnan(choices));
    r.c_prc = hgf_ar1_binary_mab_config;
    r.c_prc.n_bandits = 3;
    r.c_prc.coupled = false;
    r.c_prc.irregular_intervals = false;
    try
        [traj, infStates] = hgf_ar1_binary_mab(r, p);
        matlab_source_version = version; %#ok<NASGU>
        matlab_source_function = impl; %#ok<NASGU>
        save(fullfile(folder,[label '_matlab_result.mat']),'traj','infStates','matlab_source_version','matlab_source_function','-v7');
        fprintf('MATLAB_FORWARD_DONE %s trials=%d ignored=%d\n',label,numel(u),numel(r.ign));
    catch ex
        fprintf(2,'MATLAB_FORWARD_FAILED %s: %s\n',label,ex.identifier);
        rethrow(ex);
    end
end
end
