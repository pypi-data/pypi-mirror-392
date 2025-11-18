"""Optimizer-agnostic functions.

Normalize inputs and outputs, and build no-arbitrage constraints.
"""

import dataclasses
from typing import Optional


@dataclasses.dataclass
class Constraint:
    """No-arbitrage constraint between 1-3 option prices."""

    kind: str  # "butterfly", "calendar", "vertical"
    points: tuple[int, ...]  # indices of constraint
    bound: str = "lower"  # "lower", "upper", "fixed"
    tag: Optional[str] = None  # optional tag for debugging


def prepare_inputs(
    strikes: list[float],
    expiries: list,
    prices: list[float],
    bid_ask: Optional[dict[str, list[float]]],
    forward: Optional[dict],
    discount_factor: Optional[dict],
) -> tuple[list]:
    use_bid_ask = bid_ask is not None
    if use_bid_ask:
        bids, asks = bid_ask["bid"], bid_ask["ask"]
    else:
        bids = asks = [float("nan")] * len(prices)

    k, t, c, b, a = normalize_inputs(
        strikes, expiries, prices, bids, asks, forward, discount_factor
    )
    k, t, c, b, a = augment_normalized_inputs(k, t, c, b, a)
    k, t, c, b, a = parallel_sort(k, t, c, b, a)
    return k, t, c, b, a


def parallel_sort(*lists: list) -> tuple[list, ...]:
    """Sort lists in parallel, based on values of first list."""
    l0 = lists[0]
    idx = sorted(range(len(l0)), key=lambda i: l0[i])
    return tuple([l[i] for i in idx] for l in lists)


def normalize_inputs(
    strikes: list[float],
    expiries: list[float],
    prices: list[float],
    bids: list[float],
    asks: list[float],
    forward: Optional[dict],
    discount_factor: Optional[dict],
) -> tuple[list[float], ...]:
    """Normalize prices and convert expiries to index."""
    unique_expiries = sorted(set(expiries))
    expiry_to_index = {e: i for i, e in enumerate(unique_expiries)}
    expiry_to_forward = (
        forward if forward is not None else {e: 1.0 for e in unique_expiries}
    )
    expiry_to_discount_factor = (
        discount_factor
        if discount_factor is not None
        else {e: 1.0 for e in unique_expiries}
    )

    fwds = [expiry_to_forward[e] for e in expiries]
    dfs = [expiry_to_discount_factor[e] for e in expiries]

    k = [s / f for s, f in zip(strikes, fwds)]
    t = [expiry_to_index[e] for e in expiries]
    c = [p / (d * f) for p, d, f in zip(prices, dfs, fwds)]
    b = [b / (d * f) for b, d, f in zip(bids, dfs, fwds)]
    a = [a / (d * f) for a, d, f in zip(asks, dfs, fwds)]

    return k, t, c, b, a


def augment_normalized_inputs(
    strikes: list[float],
    expiries: list[int],
    prices: list[float],
    bids: list[float],
    asks: list[float],
) -> tuple[list[float], ...]:
    """Add strike=0, price=1 data to each expiry."""
    unique_expiries = sorted(set(expiries))
    for e in unique_expiries:
        strikes.append(0.0)
        expiries.append(e)
        prices.append(1.0)
        bids.append(1.0)
        asks.append(1.0)

    return strikes, expiries, prices, bids, asks


def build_index_sets(
    strikes: list[float], expiries: list[int]
) -> tuple[list[list[int]], list[list[int]]]:
    """Build index sets for calendar spread and butterfly constraints."""
    unique_expiries = sorted(set(expiries))

    index_sets = []  # map point to index set
    candidates_by_expiry = [[] for _ in unique_expiries]  # map expiry to candidates
    last_strike_by_expiry = [-float("inf") for _ in unique_expiries]
    for i, (t, k) in enumerate(zip(expiries, strikes)):
        index_set = [c for c in candidates_by_expiry[t] if strikes[c] < k]
        index_sets.append(index_set)

        candidates_by_expiry[t] = []  # reset
        last_strike_by_expiry[t] = k

        for t1 in unique_expiries[:t]:
            if k > last_strike_by_expiry[t1]:
                candidates_by_expiry[t1].append(i)

    last_index_sets = [
        [c for c in candidates if expiries[c] > t and strikes[c] > last_strike]
        for t, candidates, last_strike in zip(
            unique_expiries, candidates_by_expiry, last_strike_by_expiry
        )
    ]
    return index_sets, last_index_sets


def build_constraints(strikes: list[float], expiries: list[int]):
    unique_expiries = sorted(set(expiries))

    index_sets, last_index_sets = build_index_sets(strikes, expiries)

    points_by_expiry = [[] for _ in unique_expiries]  # ordered by strike
    for i, t in enumerate(expiries):
        points_by_expiry[t].append(i)

    constraints = (
        build_outright_constraints(points_by_expiry)
        + build_vs_constraints(points_by_expiry)
        + build_vb_constraints(points_by_expiry)
        + build_cs_constraints(points_by_expiry, strikes)
        + build_cvs_constraints(points_by_expiry, index_sets)
        + build_cb_constraints(points_by_expiry, index_sets, last_index_sets)
    )

    return constraints


def build_outright_constraints(points_by_expiry: list[list[int]]) -> list[Constraint]:
    return [
        Constraint(kind="outright", points=(p[0],), bound="fixed", tag="forward")
        for p in points_by_expiry
    ] + [
        Constraint(kind="outright", points=(p[-1],), tag="outright")
        for p in points_by_expiry
    ]


def build_vs_constraints(points_by_expiry: list[list[int]]) -> list[Constraint]:
    return [
        Constraint(kind="spread", points=(p[1], p[0]), bound="upper", tag="vs")
        for p in points_by_expiry
    ] + [
        Constraint(kind="spread", points=(p[i], p[i - 1]), tag="vs")
        for p in points_by_expiry
        for i in range(1, len(p))
    ]


def build_vb_constraints(points_by_expiry: list[list[int]]) -> list[Constraint]:
    return [
        Constraint(kind="butterfly", points=(p[i], p[i - 1], p[i + 1]), tag="vb")
        for p in points_by_expiry
        for i in range(1, len(p) - 1)
    ]


def build_cs_constraints(
    points_by_expiry: list[list[int]], strikes: list[float]
) -> list[Constraint]:
    n = len(strikes)
    m = len(points_by_expiry)  # num expiries
    n_strikes = [len(p) for p in points_by_expiry]  # by expiry

    current_index = [0 for _ in range(m)]  # by expiry
    current_strike = [strikes[p[0]] for p in points_by_expiry]  # by expiry

    constraints = []
    for _ in range(n):
        # gives min strike (with smallest expiry if multiple)
        t1 = min(range(m), key=lambda x: current_strike[x])
        index_1 = points_by_expiry[t1][current_index[t1]]
        for t2 in range(t1 + 1, m):
            if current_strike[t2] == current_strike[t1]:
                index_2 = points_by_expiry[t2][current_index[t2]]
                constraints.append(
                    Constraint(kind="spread", points=(index_1, index_2), tag="cs")
                )

        current_index[t1] += 1
        if current_index[t1] == n_strikes[t1]:  # no more strikes for this expiry
            current_strike[t1] = float("inf")
        else:
            current_strike[t1] = strikes[points_by_expiry[t1][current_index[t1]]]

    return constraints


def build_cvs_constraints(
    points_by_expiry: list[list[int]], index_sets: list[list[int]]
) -> list[Constraint]:
    return [
        Constraint(kind="spread", points=(index_1, index_2), tag="cvs")
        for points in points_by_expiry  # each expiry
        for index_1 in points[1:]
        for index_2 in index_sets[index_1]
    ]


def build_cb_constraints(
    points_by_expiry: list[list[int]],
    index_sets: list[list[int]],
    last_index_sets=list[list[int]],
) -> list[Constraint]:
    return (
        [
            Constraint(
                kind="butterfly", points=(points[j], index_2, points[j + 1]), tag="cb1a"
            )
            for points in points_by_expiry
            for j in range(1, len(points) - 1)
            for index_2 in index_sets[points[j]]  # index_1
        ]
        + [
            Constraint(
                kind="butterfly",
                points=(points[j - 1], points[j - 2], index_3),
                tag="cb1b",
            )
            for points in points_by_expiry
            for j in range(2, len(points))
            for index_3 in index_sets[points[j]]
        ]
        + [
            Constraint(
                kind="butterfly", points=(points[-1], points[-2], index_3), tag="cb1c"
            )
            for t, points in enumerate(points_by_expiry)
            for index_3 in last_index_sets[t]
        ]
        + [
            Constraint(
                kind="butterfly", points=(points[j], index_2, index_3), tag="cb2a"
            )
            for points in points_by_expiry
            for j in range(1, len(points) - 1)
            for index_2 in index_sets[points[j]]
            for index_3 in index_sets[points[j + 1]]
        ]
        + [
            Constraint(
                kind="butterfly", points=(points[-1], index_2, index_3), tag="cb2b"
            )
            for t, points in enumerate(points_by_expiry)
            for index_2 in index_sets[points[-1]]
            for index_3 in last_index_sets[t]
        ]
    )


def denormalize_outputs(
    strikes: list[float],
    expiries: list[int],
    prices: list[float],
    original_expiries: list,
    forward: Optional[dict],
    discount_factor: Optional[dict],
) -> tuple[list[float], list[float], list[float]]:
    unique_expiries = sorted(set(original_expiries))

    expiry_to_forward = (
        forward if forward is not None else {e: 1.0 for e in unique_expiries}
    )
    expiry_to_discount_factor = (
        discount_factor
        if discount_factor is not None
        else {e: 1.0 for e in unique_expiries}
    )

    strikes_out = expiries_out = prices_out = []
    for k, t, c in zip(strikes, expiries, prices):
        if k == 0.0:
            continue  # drop augmented

        e = unique_expiries[t]
        fwd, df = expiry_to_forward[e], expiry_to_discount_factor[e]
        strikes_out.append(k * fwd)
        expiries_out.append(e)
        prices_out.append(c * fwd * df)

    return strikes_out, expiries_out, prices_out


def outright_constraint(c1, _):
    """Expression for outright constraint."""
    return c1


def spread_constraint(c1, c2, k1, k2):
    """Expression for spread constraint."""
    return c2 - c1 if k1 == k2 else -(c1 - c2) / (k1 - k2)


def butterfly_constraint(c1, c2, c3, k1, k2, k3):
    """Expression for butterfly constraint."""
    return -(c1 - c2) / (k1 - k2) + (c3 - c1) / (k3 - k1)


CONSTRAINT_EXPRESSIONS = {
    "outright": outright_constraint,
    "spread": spread_constraint,
    "butterfly": butterfly_constraint,
}
