# Analysis protocol

## Question

How does CPU thread count affect lymph node expression-matrix PCA?

## Population, analysis and validation

Read section W19 of GSE336618. Exclude identifiers and control probes. Freeze a seeded permutation and take nested samples of 2,000, 10,000 and 30,000 cells. Normalize library sizes, log transform and compute 12 randomized PCs. Start a fresh worker per repeat. Record stage time and sampled peak process RSS at 10 ms intervals.

## Interpretation and scope

Timings describe one Windows CPU host. OS page cache can persist across processes. Explained-variance agreement tests one numerical endpoint. Nextflow and Slurm definitions are supplied; the measured runs used the local Python entry point.

## Primary output

[benchmark_runs.csv](../results/benchmark_runs.csv)

## Source

[Study or method](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE336618)
