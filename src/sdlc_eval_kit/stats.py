"""Success metrics over repeated trials.

pass@1 is the mean per-task success rate. pass^k (tau-bench, arXiv:2406.12045) is the
chance that k independent trials of the same task all succeed, estimated per task as
C(c, k) / C(n, k) and averaged over tasks.
"""

from math import comb, sqrt


def pass_at_1(outcomes: dict[str, list[bool]]) -> float:
    """Mean over tasks of the per-task success rate."""
    _check(outcomes, 1)
    return sum(sum(trials) / len(trials) for trials in outcomes.values()) / len(outcomes)


def pass_hat_k(outcomes: dict[str, list[bool]], k: int) -> float:
    """Mean over tasks of the probability that k trials all succeed."""
    _check(outcomes, k)
    return sum(comb(sum(trials), k) / comb(len(trials), k) for trials in outcomes.values()) / len(outcomes)


def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion (95% by default)."""
    if n <= 0 or not 0 <= successes <= n:
        raise ValueError(f"need 0 <= successes <= n and n > 0, got {successes}/{n}")
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def _check(outcomes: dict[str, list[bool]], k: int) -> None:
    if not outcomes:
        raise ValueError("no outcomes")
    short = [task for task, trials in outcomes.items() if len(trials) < k]
    if short:
        raise ValueError(f"fewer than {k} trials for: {', '.join(sorted(short))}")
