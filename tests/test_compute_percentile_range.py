import numpy as np
from app.components.choropleth import compute_percentile_range


def test_compute_percentile_range_basic():
    data = np.arange(1, 101, dtype=float)
    lo, hi = compute_percentile_range(data, 10, 90)
    assert lo < hi
    assert lo >= data.min()
    assert hi <= data.max()


def test_compute_percentile_range_identity_bounds():
    data = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    lo, hi = compute_percentile_range(data, 0, 100)
    assert lo == data.min()
    assert hi == data.max()
