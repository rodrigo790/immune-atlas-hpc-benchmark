"""Run the benchmark worker on a small synthetic count matrix without network."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np


class WorkerTest(unittest.TestCase):
    def test_thread_equivalence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "counts.npy"
            np.save(
                path, np.random.default_rng(4).poisson(2, (64, 20)).astype("float32")
            )
            ratios = []
            for threads in ("1", "2"):
                data = json.loads(
                    subprocess.check_output(
                        [
                            sys.executable,
                            "analysis.py",
                            "worker",
                            str(path),
                            "64",
                            threads,
                        ],
                        text=True,
                    )
                )
                self.assertGreater(data[2], 0)
                ratios.append(data[3])
            np.testing.assert_allclose(*ratios, atol=1e-5)
