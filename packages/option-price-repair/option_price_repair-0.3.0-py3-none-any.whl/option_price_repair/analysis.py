"""Useful analysis functions."""

import logging
import pathlib

from option_price_repair.repair import CONSTRAINT_EXPRESSIONS, Constraint

logger = logging.getLogger(__name__)


def detect_violated_constraints(
    constraints: list[Constraint], strikes: list[float], prices: list[float]
) -> None:
    """Log constraint and constraint violation counts."""
    count_by_tag = {}
    violations_by_tag: dict[str, list[tuple[Constraint, float]]] = {}
    for constraint in constraints:
        count_by_tag.setdefault(constraint.tag, 0)
        count_by_tag[constraint.tag] += 1

        violation = constraint_is_violated(constraint, strikes, prices)
        if violation > 0:
            violations_by_tag.setdefault(constraint.tag, [])
            violations_by_tag[constraint.tag].append((constraint, violation))

    for tag, count in count_by_tag.items():
        values = [value for _, value in violations_by_tag.get(tag, [])]
        if len(values) > 0:
            max_violation, mean_violation = max(values), sum(values) / len(values)
            violations_info = f" Max: {max_violation:.3g}; mean: {mean_violation:.3g}"
        else:
            violations_info = ""
        logger.info(
            f"Constraint {tag}: {count} constraints, {len(values)} violations.{violations_info}"
        )


def constraint_is_violated(
    constraint: Constraint, strikes: list[float], prices: list[float]
) -> float:
    """Check if a constraint is violated.

    Return the magnitude of the violation if so, and a number <= 0 if not.
    """
    constraint_func = CONSTRAINT_EXPRESSIONS[constraint.kind]
    c = [prices[i] for i in constraint.points]
    k = [strikes[i] for i in constraint.points]
    value = constraint_func(*c, *k)

    if constraint.bound == "lower":
        return -value  # violation if <0
    elif constraint.bound == "upper":
        return value - 1  # violation if >1
    elif constraint.bound == "fixed":
        return abs(value - 1)  # violation if != 1
    else:
        raise ValueError(f"unsupported bound type: {constraint.bound}")


def plot_perturbations(
    strikes: list[float],
    expiries: list[int],
    prices: list[float],
    perturbations: list[float],
    output_dir: str,
    tags: tuple[str, ...] = (),
):
    try:
        import plotly.express as px
        import polars as pl
    except ImportError as e:
        raise ImportError(
            "Could not import dependencies for plotting."
            " Did you install the analysis dependency group?"
        ) from e

    unique_expiries = [str(i + 1) for i in sorted(set(expiries))]
    expiries_str = [str(i + 1) for i in expiries]

    x, y, colour = "Strike/Forward", "Perturbation", "Expiry"
    title = "Relative perturbations by expiry"
    data = (
        pl.DataFrame(
            (
                pl.Series(x, strikes),
                pl.Series("abs_perturbation", perturbations),
                pl.Series("prices", prices),
                pl.Series(colour, expiries_str, dtype=pl.Enum(unique_expiries)),
            )
        )
        .with_columns(pl.col("abs_perturbation").truediv(pl.col("prices")).alias(y))
        .filter(pl.col(x).gt(0))
    )

    plot = px.scatter(data, x=x, y=y, color=colour, title=title)

    file_tags = "-".join(t.lower().replace(" ", "_") for t in ("perturbations",) + tags)
    plot.write_html(pathlib.Path(output_dir) / f"{file_tags}.html")
