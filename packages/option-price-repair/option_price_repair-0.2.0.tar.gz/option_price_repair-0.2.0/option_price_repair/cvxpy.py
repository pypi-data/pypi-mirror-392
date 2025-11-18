"""`cvxpy`-based solver implementation."""

try:
    import cvxpy as cp
except ImportError as e:
    raise ImportError(
        "Could not import cvxpy. Did you install the cvxpy dependency group?"
    ) from e

from option_price_repair.repair import CONSTRAINT_EXPRESSIONS, Constraint


def optimize(
    constraints: list[Constraint],
    strikes: list[float],
    prices: list[float],
    bids: list[float],
    asks: list[float],
    use_bid_ask: bool,
    solver: str = cp.CLARABEL,
    verbose: bool = False,
) -> list[float]:
    if use_bid_ask:
        return optimize_bid_ask(
            constraints, strikes, prices, bids, asks, solver, verbose=verbose
        )
    else:
        return optimize_simple(constraints, strikes, prices, solver, verbose=verbose)


def optimize_simple(
    constraints: list[Constraint],
    strikes: list[float],
    prices: list[float],
    solver: str,
    verbose: bool = False,
) -> list[float]:
    n = len(prices)

    # define variables
    e_plus = cp.Variable(n, nonneg=True)
    e_minus = cp.Variable(n, nonneg=True)
    perturbations = e_plus - e_minus

    objective = cp.Minimize(cp.sum(e_plus) + cp.sum(e_minus))

    constraints_resolved = [
        constraint_to_cvxpy(c, strikes, prices, perturbations) for c in constraints
    ]

    problem = cp.Problem(objective, constraints_resolved)
    problem.solve(solver=solver, verbose=verbose)
    print(problem.solver_stats)

    if problem.status != cp.OPTIMAL:
        raise RuntimeError("non-optimal result")

    return perturbations.value.tolist()


def optimize_bid_ask(
    constraints: list[Constraint],
    strikes: list[float],
    prices: list[float],
    bids: list[float],
    asks: list[float],
    solver: str,
    verbose: bool = False,
):
    n = len(prices)

    perturbations = cp.Variable(n)
    auxiliary = cp.Variable(n)

    objective = cp.Minimize(cp.sum(auxiliary))

    arbitrage_constraints = [
        constraint_to_cvxpy(c, strikes, prices, perturbations) for c in constraints
    ]
    bid_ask_constraints = cvxpy_bid_ask_constraints(
        perturbations, auxiliary, prices, bids, asks
    )

    constraints_resolved = arbitrage_constraints + bid_ask_constraints

    problem = cp.Problem(objective, constraints_resolved)
    problem.solve(solver=solver, verbose=verbose)

    if problem.status != cp.OPTIMAL:
        raise RuntimeError("non-optimal result")

    return perturbations.value.tolist()


def constraint_to_cvxpy(
    constraint: Constraint,
    strikes: list[float],
    prices: list[float],
    perturbations: cp.Variable,  # size n
):
    constraint_func = CONSTRAINT_EXPRESSIONS[constraint.kind]
    c = [prices[i] + perturbations[i] for i in constraint.points]
    k = [strikes[i] for i in constraint.points]

    expression = constraint_func(*c, *k)
    if constraint.bound == "lower":
        return expression >= 0
    elif constraint.bound == "upper":
        return expression <= 1
    elif constraint.bound == "fixed":
        return expression == 1
    else:
        raise ValueError(f"unsupported bound type: {constraint.bound}")


def cvxpy_bid_ask_constraints(
    perturbations: cp.Variable,
    auxiliary: cp.Variable,
    prices: list[float],
    bids: list[float],
    asks: list[float],
):
    n = len(prices)
    bid_spreads = [c - b for c, b in zip(prices, bids)]
    ask_spreads = [a - c for c, a in zip(prices, asks)]

    valid_bid_spreads = [s for s in bid_spreads if s > 0]
    valid_ask_spreads = [s for s in ask_spreads if s > 0]
    d0 = max(1e-8, min(1 / n, min(valid_bid_spreads), min(valid_ask_spreads)))
    # d0 = objective when price is perturbed to bid/ask

    constraints = []
    for e, t, sb, sa in zip(perturbations, auxiliary, bid_spreads, ask_spreads):
        constraints.append(-e - sb + d0 <= t)
        constraints.append(e - sa + d0 <= t)
        if sb > 0:
            constraints.append(-d0 / sb * e <= t)
        if sa > 0:
            constraints.append(d0 / sa * e <= t)

    return constraints
