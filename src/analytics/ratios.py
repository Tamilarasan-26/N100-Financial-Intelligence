import logging


logger = logging.getLogger(__name__)


def net_profit_margin(
    net_profit,
    sales
):
    """
    Calculate Net Profit Margin.

    Formula:
        net_profit / sales * 100

    Returns None when sales is zero.
    """

    if sales == 0:
        return None

    return (
        net_profit / sales
    ) * 100


def operating_profit_margin(
    operating_profit,
    sales,
    source_opm=None
):
    """
    Calculate Operating Profit Margin and optionally
    cross-check against a valid source OPM percentage.

    Formula:
        operating_profit / sales * 100

    Source OPM values outside the percentage-like
    range of -100 to 100 are treated as semantically
    incompatible source values and are excluded from
    the cross-check.

    A warning is logged when a valid source OPM differs
    from the calculated OPM by more than 1 percentage
    point.

    Returns None when sales is zero.
    """

    if sales == 0:
        return None

    calculated_opm = (
        operating_profit / sales
    ) * 100

    source_opm_is_valid = (
        source_opm is not None
        and -100 <= source_opm <= 100
    )

    if source_opm_is_valid:
        difference = abs(
            calculated_opm - source_opm
        )

        if difference > 1:
            logger.warning(
                "OPM cross-check mismatch: "
                "calculated=%.4f, "
                "source=%.4f, "
                "difference=%.4f",
                calculated_opm,
                source_opm,
                difference
            )

    return calculated_opm


def return_on_equity(
    net_profit,
    equity_capital,
    reserves
):
    """
    Calculate Return on Equity.

    Formula:
        net_profit /
        (equity_capital + reserves) * 100

    Returns None when total equity is zero
    or negative.
    """

    total_equity = (
        equity_capital
        + reserves
    )

    if total_equity <= 0:
        return None

    return (
        net_profit / total_equity
    ) * 100


def return_on_capital_employed(
    ebit,
    equity_capital,
    reserves,
    borrowings
):
    """
    Calculate Return on Capital Employed.

    Formula:
        EBIT /
        (
            equity_capital
            + reserves
            + borrowings
        ) * 100

    Returns None when capital employed is zero
    or negative.
    """

    capital_employed = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital_employed <= 0:
        return None

    return (
        ebit / capital_employed
    ) * 100


def return_on_assets(
    net_profit,
    total_assets
):
    """
    Calculate Return on Assets.

    Formula:
        net_profit / total_assets * 100

    Returns None when total assets is zero.
    """

    if total_assets == 0:
        return None

    return (
        net_profit / total_assets
    ) * 100


def is_roce_above_benchmark(
    roce,
    broad_sector,
    sector_benchmark=None,
    absolute_threshold=15
):
    """
    Evaluate ROCE.

    Financial companies use a sector-relative
    benchmark.

    Non-financial companies use an absolute
    ROCE threshold.
    """

    if roce is None:
        return False

    if broad_sector == "Financials":
        if sector_benchmark is None:
            return False

        return roce > sector_benchmark

    return roce > absolute_threshold


def debt_to_equity(
    total_debt,
    equity_capital,
    reserves
):
    """
    Calculate Debt-to-Equity ratio.

    Formula:
        total_debt /
        (equity_capital + reserves)

    Debt-free companies return 0.

    Invalid zero or negative equity returns None.
    """

    total_equity = (
        equity_capital
        + reserves
    )

    if total_debt == 0:
        return 0

    if total_equity <= 0:
        return None

    return (
        total_debt / total_equity
    )


def high_leverage_flag(
    debt_equity,
    broad_sector,
    threshold=2
):
    """
    Flag highly leveraged companies.

    Financial-sector companies are excluded
    from the standard Debt-to-Equity warning.
    """

    if debt_equity is None:
        return False

    if broad_sector == "Financials":
        return False

    return debt_equity > threshold


def interest_coverage_ratio(
    ebit,
    interest
):
    """
    Calculate Interest Coverage Ratio.

    Formula:
        EBIT / Interest

    Returns None when interest is zero.
    """

    if interest == 0:
        return None

    return (
        ebit / interest
    )


def interest_coverage_label(
    interest_coverage,
    interest
):
    """
    Return Interest Coverage classification.

    Zero interest is classified as Debt Free.
    """

    if interest == 0:
        return "Debt Free"

    if (
        interest_coverage is not None
        and interest_coverage < 1.5
    ):
        return "Warning"

    return "Normal"


def low_interest_coverage_flag(
    interest_coverage,
    interest
):
    """
    Flag Interest Coverage Ratio values below 1.5.

    Debt-free companies are not flagged.
    """

    if interest == 0:
        return False

    if interest_coverage is None:
        return False

    return (
        interest_coverage < 1.5
    )


def net_debt(
    total_debt,
    cash_and_equivalents
):
    """
    Calculate Net Debt.

    Formula:
        total_debt - cash_and_equivalents
    """

    return (
        total_debt
        - cash_and_equivalents
    )


def asset_turnover(
    sales,
    total_assets
):
    """
    Calculate Asset Turnover.

    Formula:
        sales / total_assets

    Returns None when total assets is zero.
    """

    if total_assets == 0:
        return None

    return (
        sales / total_assets
    )