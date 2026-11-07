function optimizer_trace_subject7_matlab(root,toolbox_root,original,output_path)
% Untimed original subject-7 PUBLIC fitModel trace; no source modifications.
% This experiment is distinct from archived 64-subject run 41863441006.
addpath(genpath(toolbox_root));
hgfx='4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27';
ref='2437f4dc241541072722a2695ddeca7b44d83dd3';
src=jsondecode(fileread(fullfile(original,'summary-41863441006.json')));
if ~strcmp(src.hgfx_sha,hgfx) || ~strcmp(src.matlab_sha,ref)
    error('hgfx:perf01:identity','Wrong original fit source SHAs');
end
raw=jsondecode(fileread(fullfile(original,'matlab_raw.json')));
old=raw.cases(8);
if old.subject_index_zero_based~=7 || ...
   ~strcmp(old.status,'MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION')
    error('hgfx:perf01:subject','Original subject 7 missing/failed');
end
data=jsondecode(fileread(fullfile(root,'inputs','binary_128_s64.json')));
if ~isequal(size(data.u),[64,128]) || ~isequal(size(data.y),[64,128])
    error('hgfx:perf01:data','Original unchanged 64x128 input required');
end
settings=quasinewton_optim_config();
if settings.maxIter ~= 100 || ~settings.optIter || settings.nRandInit ~= 0
    error('hgfx:perf01:optimizer','Original optimizer options changed');
end
u=double(data.u(8,:))';
y=double(data.y(8,:))';
% Capturing output is outside any timing region; preserve original public API.
text=evalc(['fit=fitModel(y,u,' ...
    '''hgf_binary_config'',''unitsq_sgm_config'',' ...
    '''quasinewton_optim_config'');']);
if ~isfield(fit.optim,'iter') || ~isstruct(fit.optim.iter) || ...
   ~isfield(fit.optim.iter,'x') || ~isfield(fit.optim.iter,'val')
    error('hgfx:perf01:trace','Frozen public MATLAB optimizer history missing');
end
same_start=isequaln(fit.optim.init(:),double(old.optim.init(:))) && ...
    fit.c_opt.nRandInit==0;
out=struct();
out.schema='perf01-subject7-optimizer-trace-matlab-v1';
out.status='FULL_PUBLIC_FIT_TRACE_EXPORTED';
out.model='hgf_binary';
out.trials=128;
out.subject_index_zero_based=7;
out.source_run_id='41863441006';
out.frozen_hgfx_sha=hgfx;
out.frozen_matlab_sha=ref;
out.source_input_sha256=src.hgfx_input_sha256;
out.source_config_sha256=src.hgfx_config_sha256;
out.original_raw_fits_verified=true;
out.frozen_start_matches=same_start;
out.n_rand_init=double(fit.c_opt.nRandInit);
out.fit_neg_lj=double(fit.optim.negLj);
out.original_final_full=old.optim.final;
out.final_full=fit.optim.final;
out.iter_x=fit.optim.iter.x;
out.iter_val=fit.optim.iter.val;
out.fitModel_function_path=which('fitModel');
out.quasinewton_function_path=which('quasinewton_optim');
out.console_characters=numel(text);
out.note='Untimed public MATLAB fitModel with preallocated iter arrays; MATLAB does not expose a termination reason.';
[d,~,~]=fileparts(output_path);
if ~isfolder(d);mkdir(d);end
fid=fopen(output_path,'w');
if fid<0;error('hgfx:perf01:output','Cannot open source trace output');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(out));
fprintf('Archived fresh public MATLAB trace; allocated slots=%d, finite values=%d, not number of executed iterations.\n', ...
    numel(fit.optim.iter.val),sum(isfinite(fit.optim.iter.val)));
end
