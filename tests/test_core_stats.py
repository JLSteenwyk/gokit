from __future__ import annotations

from gokit.core.stats import bh_adjust, fisher_left_tail, fisher_right_tail


def test_fisher_right_tail_basic_range() -> None:
    p = fisher_right_tail(pop_n=100, pop_count=20, study_n=10, study_count=5)
    assert 0.0 <= p <= 1.0


def test_fisher_right_tail_zero_cases() -> None:
    assert fisher_right_tail(pop_n=0, pop_count=0, study_n=0, study_count=0) == 1.0
    assert fisher_right_tail(pop_n=10, pop_count=0, study_n=5, study_count=0) == 1.0


def test_fisher_left_tail_basic_range() -> None:
    p = fisher_left_tail(pop_n=100, pop_count=20, study_n=10, study_count=1)
    assert 0.0 <= p <= 1.0


def test_fisher_left_tail_bounds() -> None:
    assert fisher_left_tail(pop_n=0, pop_count=0, study_n=0, study_count=0) == 1.0
    assert fisher_left_tail(pop_n=10, pop_count=0, study_n=5, study_count=0) == 1.0


def test_bh_adjust_monotonic_bounds() -> None:
    vals = [0.01, 0.2, 0.03, 0.5]
    adj = bh_adjust(vals)
    assert len(adj) == len(vals)
    for p in adj:
        assert 0.0 <= p <= 1.0
