from __future__ import annotations

from gokit.core.stats import adjust_pvalues, bh_adjust, fisher_left_tail, fisher_right_tail


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


def test_adjust_pvalues_supported_methods() -> None:
    vals = [0.01, 0.02, 0.5]
    out_bh = adjust_pvalues(vals, "fdr_bh")
    out_by = adjust_pvalues(vals, "fdr_by")
    out_bonf = adjust_pvalues(vals, "bonferroni")
    out_holm = adjust_pvalues(vals, "holm")
    out_none = adjust_pvalues(vals, "none")

    assert len(out_bh) == len(vals)
    assert len(out_by) == len(vals)
    assert len(out_bonf) == len(vals)
    assert len(out_holm) == len(vals)
    assert out_none == vals
    assert out_bonf[1] > out_bh[1]
    assert out_by[0] >= out_bh[0]
    assert out_holm[1] >= out_bh[1]


def test_adjust_pvalues_rejects_unknown_method() -> None:
    try:
        adjust_pvalues([0.1, 0.2], "not_a_method")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for unsupported method")
