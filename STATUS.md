# Execution record

Execution date: 2026-11-26. Analysis completed with public research inputs. The exact input bytes are recorded in [the data manifest](data/sources.json). The reproduction commands are in [README.md](README.md).

At 30,000 cells and 1,000 targets, median PCA time over three fresh processes fell from 2.12 s with one thread to 0.88 s with four. All 27 runs met the 10⁻⁵ explained-variance-ratio tolerance.

Timings describe one Windows CPU host. OS page cache can persist across processes. Explained-variance agreement tests one numerical endpoint. The measured CPU runs used the local Python entry point. The Slurm profile remains untested on a cluster.

[Repository and current commit history](https://github.com/rodrigo790/immune-atlas-hpc-benchmark/commits/main) · [Continuous integration](https://github.com/rodrigo790/immune-atlas-hpc-benchmark/actions)


The local benchmark ran on an Intel Core Ultra 9 185H. [Stage medians, speedup and parallel efficiency](results/stage_scaling.csv) and [software and hardware](results/environment.json) accompany the raw timings. The Actions workflow also runs the Nextflow worker on a synthetic matrix.
