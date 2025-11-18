"""Repair arbitrage in option prices."""

import logging
from typing import Literal, Optional, Union

from option_price_repair.analysis import detect_violated_constraints, plot_perturbations
from option_price_repair.repair import (
    build_constraints,
    denormalize_outputs,
    prepare_inputs,
)

SupportedOptimizer = Literal["cvxpy"]

logger = logging.getLogger(__name__)


def repair(
    strikes: list[float],
    expiries: Union[list[float], list[int]],
    prices: list[float],
    bid_ask: Optional[tuple[list[float], list[float]]] = None,
    forward: Optional[dict] = None,
    discount_factor: Optional[dict] = None,
    optimizer: SupportedOptimizer = "cvxpy",
    verbose: bool = False,  # print constraint violations and optimizer logs
    plot: bool = False,  # plot perturbations
    output_dir: Optional[str] = None,  # write perturbation plot here
) -> tuple[list[float], list, list[float]]:
    """Perturb option prices to ensure no-arbitrage conditions are satisfied.

    This function assumes valid inputs; i.e. it does not do validation.

    Input strikes, expiries, call prices etc as python lists of the same size.
    `bid_ask` is a tuple (bid_prices, ask_prices). `forward` is a dictionary
    mapping each expiry to the corresponding forward price; similar for
    `discount_factor`.

    `verbose` controls whether constraint violations and optimizer logs are
    printed.

    `plot` determines whether optimal perturbations are plotted to `output_dir`.

    Returns original strikes and expiries, and repaired prices; possibly
    in a different order.
    """
    k, t, c, b, a = prepare_inputs(
        strikes, expiries, prices, bid_ask, forward, discount_factor
    )

    constraints = build_constraints(k, t)

    if verbose:
        logger.info("-----------Constraint violations before optimization-------------")
        detect_violated_constraints(constraints, k, c)

    use_bid_ask = bid_ask is not None
    if optimizer == "cvxpy":
        import option_price_repair.cvxpy

        perturbations = option_price_repair.cvxpy.optimize(
            constraints, k, c, b, a, use_bid_ask, verbose=verbose
        )
    else:
        raise ValueError(f"Unsupported optimizer: {optimizer}")

    repaired = [p + d for p, d in zip(c, perturbations)]

    if verbose:
        logger.info("------------Constraint violations after optimization-------------")
        detect_violated_constraints(constraints, k, repaired)

    if plot:
        if output_dir is None:
            raise ValueError("output_dir must be specified to plot perturbations")
        tags = ("bid_ask",) if use_bid_ask else ()
        plot_perturbations(k, t, c, perturbations, output_dir, tags)

    k, t, c = denormalize_outputs(k, t, repaired, expiries, forward, discount_factor)

    return k, t, c
