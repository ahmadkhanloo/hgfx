# GPU Architecture

## Goals

- keep data and optimizer state on device;
- batch independent fits;
- avoid Python loops in hot paths;
- compile by model signature;
- support heterogeneous trial lengths through bucketing/padding/masks.

## Execution shape

```text
subjects × restarts
        ↓ vmap
trial recursion
        ↓ scan
model equations
        ↓ jit
GPU
```

## Compile cache signature

At minimum:
- model topology;
- number of levels;
- response model;
- dtype;
- trial-length bucket;
- static model options.

## Multi-GPU

Start with independent data-parallel batches. Do not introduce model parallelism unless profiling proves it necessary.
