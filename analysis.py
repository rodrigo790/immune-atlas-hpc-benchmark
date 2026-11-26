"""CPU scaling on mouse lymph node CosMx cell counts, GEO GSE336618."""

import time
import platform
import subprocess
import sys
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from inputs import source, OUT

BASE = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE336nnn/GSE336618/suppl/"


def transform(x):
    return np.log1p(1e4 * x / np.maximum(x.sum(axis=1, keepdims=True), 1))


def worker(path, n, threads):
    import psutil
    import threading

    process = psutil.Process()
    peak = [process.memory_info().rss]
    stop = threading.Event()

    def sample():
        while not stop.wait(0.01):
            peak[0] = max(peak[0], process.memory_info().rss)

    monitor = threading.Thread(target=sample)
    monitor.start()
    try:
        with threadpool_limits(limits=threads):
            x = np.load(path, mmap_mode="r")[:n]
            start = time.perf_counter()
            z = transform(x)
            norm_time = time.perf_counter() - start
            start = time.perf_counter()
            pca = PCA(n_components=12, svd_solver="randomized", random_state=42).fit(z)
            pca_time = time.perf_counter() - start
        print(
            json.dumps(
                [
                    norm_time,
                    pca_time,
                    peak[0] / 2**20,
                    pca.explained_variance_ratio_.tolist(),
                ]
            )
        )
    finally:
        stop.set()
        monitor.join()


def main():
    path = source(BASE + "GSE336618_W19_exprMat_file.csv.gz")
    d = pd.read_csv(path, dtype=np.int32)
    markers = [
        c
        for c in d
        if c not in ("cell_ID", "fov")
        and not c.lower().startswith(
            ("negpr", "negative", "systemcontrol", "falsecode")
        )
    ]
    x = d[markers].to_numpy(dtype=np.float32)
    cache = path.parent / "w19_shuffled.npy"
    np.save(cache, x[np.random.default_rng(42).permutation(len(x))])
    rows = []
    checks = []
    for n in sorted({min(len(x), s) for s in (2000, 10000, 30000)}):
        reference = None
        for threads in (1, 2, 4):
            for rep in range(3):
                cmd = [
                    sys.executable,
                    __file__,
                    "worker",
                    str(cache),
                    str(n),
                    str(threads),
                ]
                norm, pca, rss, ratio = json.loads(
                    subprocess.check_output(cmd, text=True)
                )
                if reference is None:
                    reference = np.array(ratio)
                delta = np.max(np.abs(reference - ratio))
                checks.append([n, threads, rep, delta, delta < 1e-5])
                rows.append(
                    [
                        n,
                        len(markers),
                        threads,
                        rep,
                        norm,
                        pca,
                        rss,
                        platform.machine(),
                        platform.system(),
                    ]
                )
    df = pd.DataFrame(
        rows,
        columns=[
            "cells",
            "features",
            "threads",
            "repeat",
            "normalize_s",
            "pca_s",
            "peak_rss_MiB",
            "machine",
            "os",
        ],
    )
    df.to_csv(OUT / "benchmark_runs.csv", index=False)
    eq = pd.DataFrame(
        checks,
        columns=["cells", "threads", "repeat", "max_variance_ratio_difference", "pass"],
    )
    eq.to_csv(OUT / "scientific_equivalence.csv", index=False)
    fig, ax = plt.subplots(1, 2, figsize=(9, 4))
    for n, g in df.groupby("cells"):
        med = g.groupby("threads").median(numeric_only=True)
        ax[0].plot(med.index, med.pca_s, "o-", label=f"{n:,}")
        ax[1].plot(med.index, med.peak_rss_MiB, "o-")
    for a in ax:
        a.set_xlabel("BLAS threads")
    ax[0].set_ylabel("Median PCA time (s)")
    ax[1].set_ylabel("Median peak process RSS (MiB)")
    ax[0].legend(title="Cells")
    fig.tight_layout()
    fig.savefig(OUT / "scaling.png", dpi=160)
    if not eq["pass"].all():
        raise ValueError("PCA variance tolerance exceeded")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        worker(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    else:
        main()
