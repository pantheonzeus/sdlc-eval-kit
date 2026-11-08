import pytest

from sdlc_eval_kit.stats import pass_at_1, pass_hat_k, wilson


def test_pass_at_1_is_mean_of_task_rates():
    outcomes = {"a": [True, True, True], "b": [True, False, False], "c": [False, False, False]}
    assert pass_at_1(outcomes) == pytest.approx((1 + 1 / 3 + 0) / 3)


def test_pass_hat_k_needs_every_trial():
    outcomes = {"a": [True, True, True], "b": [True, True, False]}
    assert pass_hat_k(outcomes, 3) == pytest.approx(0.5)
    assert pass_hat_k(outcomes, 1) == pytest.approx(pass_at_1(outcomes))


def test_pass_hat_k_unbiased_estimator():
    # 3 of 4 trials passed: C(3,2)/C(4,2) = 3/6
    assert pass_hat_k({"a": [True, True, True, False]}, 2) == pytest.approx(0.5)


def test_pass_hat_k_is_never_above_pass_at_1():
    outcomes = {"a": [True, False, True], "b": [True, True, True], "c": [False, True, False]}
    assert pass_hat_k(outcomes, 3) <= pass_at_1(outcomes)


def test_too_few_trials_rejected():
    with pytest.raises(ValueError, match="fewer than 3"):
        pass_hat_k({"a": [True, True]}, 3)
    with pytest.raises(ValueError):
        pass_at_1({})


def test_wilson_known_values():
    low, high = wilson(5, 10)
    assert low == pytest.approx(0.2366, abs=1e-4)
    assert high == pytest.approx(0.7634, abs=1e-4)


def test_wilson_edges_stay_in_range():
    assert wilson(0, 10)[0] == 0.0
    assert wilson(10, 10)[1] == 1.0
    assert 0 < wilson(0, 10)[1] < 0.35
    with pytest.raises(ValueError):
        wilson(3, 2)
