"""Median stage time, scaling and sampled resident memory by problem size."""

import platform
import subprocess
import sys
import json
import psutil
import pandas as pd
import numpy as np
from threadpoolctl import threadpool_info
from inputs import OUT


def main():
    d = pd.read_csv(OUT / "benchmark_runs.csv")
    med = (
        d.groupby(["cells", "threads"])[["normalize_s", "pca_s", "peak_rss_MiB"]]
        .median()
        .reset_index()
    )
    base = med[med.threads == 1].set_index("cells")
    for stage in ("normalize", "pca"):
        med[stage + "_speedup"] = med.cells.map(base[stage + "_s"]) / med[stage + "_s"]
        med[stage + "_efficiency"] = med[stage + "_speedup"] / med.threads
    med.to_csv(OUT / "stage_scaling.csv", index=False)
    # Capture generic device information without user or host identifiers.
    vendor = platform.processor()
    if sys.platform == "win32":
        try:
            vendor = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_Processor).Name",
                ],
                text=True,
            ).strip()
        except (OSError, subprocess.SubprocessError):
            pass
    record = dict(
        cpu=vendor,
        physical_cores=psutil.cpu_count(logical=False),
        logical_cpus=psutil.cpu_count(),
        ram_GiB=round(psutil.virtual_memory().total / 2**30, 1),
        python=platform.python_version(),
        system=platform.system(),
        blas=[
            {
                k: v
                for k, v in info.items()
                if k in ("internal_api", "version", "architecture")
            }
            for info in threadpool_info()
        ],
    )
    (OUT / "environment.json").write_text(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
