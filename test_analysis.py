import unittest
import numpy as np
from analysis import transform


class NormalizeTest(unittest.TestCase):
    def test_zero_and_library_size(self):
        z = transform(np.array([[0.0, 0], [1, 2], [2, 4]]))
        np.testing.assert_allclose(z[0], [0, 0])
        np.testing.assert_allclose(z[1], z[2])
