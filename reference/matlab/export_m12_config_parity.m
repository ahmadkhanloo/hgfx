function export_m12_config_parity(output_path)
%EXPORT_M12_CONFIG_PARITY Config/prior parity for all M12-added families.
repo_root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
hgf_root=fullfile(repo_root,'external','hgf-toolbox');
addpath(hgf_root); addpath(fullfile(hgf_root,'core'));
addpath(fullfile(hgf_root,'building_blocks')); addpath(fullfile(hgf_root,'perceptual'));
addpath(fullfile(hgf_root,'observation')); addpath(fullfile(hgf_root,'utilities'));

payload=struct;
payload.metadata.schema_version='m12-config-1';
payload.metadata.reference_version='8.2.0';
payload.metadata.reference_commit='2437f4dc241541072722a2695ddeca7b44d83dd3';

names={...
'hgf_ar1_config',...
'hgf_binary_mab_config','hgf_ar1_mab_config',...
'hgf_ar1_binary_mab_config','ehgf_ar1_binary_mab_config','uhgf_ar1_binary_mab_config',...
'hgf_jget_config','ehgf_jget_config','uhgf_jget_config',...
'hgf_categorical_config','hgf_categorical_norm_config','hgf_whatworld_config','hgf_whichworld_config',...
'bayes_optimal_config','bayes_optimal_binary_config','bayes_optimal_categorical_config',...
'bayes_optimal_whatworld_config','bayes_optimal_whichworld_config',...
'rs_belief_config','rs_precision_config','rs_precision_whatworld_config','rs_surprise_config',...
'squared_pe_config',...
'condhalluc_obs_config','condhalluc_obs2_config','condhalluc_obs3_config',...
'softmax_wld_config','softmax_mu3_wld_config','logrt_linear_whatworld_config'};

for i=1:length(names)
    name=names{i}; c=feval(name);
    s=struct; s.priormus=encode_vec(c.priormus); s.priorsas=encode_vec(c.priorsas);
    opts={'n_levels','n_bandits','coupled','irregular_intervals','update_type',...
          'n_outcomes','n_states','nw','kaub','thub','predorpost'};
    for j=1:length(opts)
        key=opts{j};
        if isfield(c,key), s.(key)=c.(key); end
    end
    payload.configs.(name)=s;
end

% HHMM config has frozen function/file name mismatch. Patch only the name.
tmpdir=tempname; mkdir(tmpdir);
src=fileread(fullfile(hgf_root,'perceptual','tapas_hhmm_config.m'));
src=strrep(src,'function c = hhmm_config','function c = tapas_hhmm_config');
src=strrep(src,'@hhmm','@tapas_hhmm');
src=strrep(src,'@hhmm_transp','@tapas_hhmm_transp');
fidtmp=fopen(fullfile(tmpdir,'tapas_hhmm_config.m'),'w'); fwrite(fidtmp,src); fclose(fidtmp);
addpath(tmpdir,'-begin'); clear tapas_hhmm_config;
c=tapas_hhmm_config;
payload.configs.tapas_hhmm_config=struct('priormus',encode_vec(c.priormus),'priorsas',encode_vec(c.priorsas),'n_outcomes',c.n_outcomes);
rmpath(tmpdir); clear tapas_hhmm_config;
payload.source_repairs.tapas_hhmm_config='function/file name aligned';

outdir=fileparts(output_path);
if ~isempty(outdir)&&~exist(outdir,'dir'),mkdir(outdir);end
fid=fopen(output_path,'w');
if fid==-1,error('hgfx:m12config:openFailed','Could not open output');end
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(payload,'PrettyPrint',true));
fprintf('HGFX M12 config export: PASS\n');
end


function s=encode_vec(v)
v=v(:)';
kind=zeros(size(v));
kind(isnan(v))=1;
kind(isinf(v) & v>0)=2;
kind(isinf(v) & v<0)=-2;
values=v;
values(kind~=0)=0;
s=struct('values',values,'kind',kind);
end
