function out = hgfx_json_ieee(value)
%HGFX_JSON_IEEE Lossless nonfinite transport for real scientific arrays.
% MATLAB jsonencode normally maps NaN and both signed infinities to null.
% Convert only numeric arrays containing nonfinite values into same-shape
% cell arrays with explicit IEEE strings. Finite values remain JSON numbers.
if isstruct(value)
    out = value;
    names = fieldnames(value);
    for k = 1:numel(value)
        for j = 1:numel(names)
            out(k).(names{j}) = hgfx_json_ieee(value(k).(names{j}));
        end
    end
elseif iscell(value)
    out = cellfun(@hgfx_json_ieee, value, 'UniformOutput', false);
elseif isnumeric(value) && any(~isfinite(value(:)))
    assert(isreal(value), 'hgfx:json:complex', 'Complex arrays require a separate schema');
    out = num2cell(value);
    out(isnan(value)) = {'NaN'};
    out(isinf(value) & value > 0) = {'Infinity'};
    out(isinf(value) & value < 0) = {'-Infinity'};
else
    out = value;
end
end
