import pytest
from numericals import ode

import math

f1 = lambda x, y: y


def test_euler():
    f1_euler = ode.euler(f1, 0, 1, 1, 10_000)

    assert f1_euler[0] == pytest.approx((0, 1), abs=1e-3)
    assert f1_euler[-1] == pytest.approx((1, math.e), abs=1e-3)


def test_heun():
    f1_heun = ode.heun(f1, 0, 1, 1, 10_000)

    assert f1_heun[0] == pytest.approx((0, 1), abs=1e-3)
    assert f1_heun[-1] == pytest.approx((1, math.e), abs=1e-3)


def test_rk4():
    f1_rk4 = ode.rk4(f1, 0, 1, 1, 10_000)

    assert f1_rk4[0] == pytest.approx((0, 1), abs=1e-3)
    assert f1_rk4[-1] == pytest.approx((1, math.e), abs=1e-3)
