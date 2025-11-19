"""Tests for pyoptimize core functions."""

from pylib-optimize import gradient_descent


def test_gradient_descent():
    def f(x):
        return x ** 2
    result = gradient_descent(f, 5.0, learning_rate=0.1, iterations=50)
    assert abs(result) < 1.0
