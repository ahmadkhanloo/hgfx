function y = binornd(n, p, varargin)
%BINORND M11 test-only Bernoulli shim for MATLAB Actions without Statistics Toolbox.
% This helper is intentionally scoped to reference/matlab/m11_shims and is
% added to the path only by the M11 exporter. HGFX does not claim RNG-stream
% identity with the Statistics Toolbox implementation.
if ~isscalar(n) || n ~= 1
    error('hgfx:m11:binorndShim','M11 shim supports Bernoulli n=1 only.');
end
if ~isempty(varargin)
    error('hgfx:m11:binorndShim','M11 shim does not support explicit output sizes.');
end
if any(p(:) < 0 | p(:) > 1 | isnan(p(:)))
    error('hgfx:m11:binorndShim','Probability must be finite and in [0,1].');
end
y = double(rand(size(p)) < p);
end
