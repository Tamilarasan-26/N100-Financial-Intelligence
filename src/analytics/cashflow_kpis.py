from dataclasses import dataclass
from typing import Optional


STRONG = "STRONG"
ADEQUATE = "ADEQUATE"
WEAK = "WEAK"
NOT_AVAILABLE = "NOT_AVAILABLE"


@dataclass(frozen=True)
class CFOQualityResult:
    score: Optional[float]
    label: str


def free_cash_flow(
    operating_cash_flow,
    capex
):
    """
    Calculate Free Cash Flow.

    Formula:
        FCF = CFO - CapEx
    """

    if (
        operating_cash_flow is None
        or capex is None
    ):
        return None

    return operating_cash_flow - capex


def cfo_quality_score(
    operating_cash_flow,
    net_profit
):
    """
    Calculate CFO Quality Score.

    Formula:
        CFO / Net Profit

    Classification:
        > 1.0       = STRONG
        0.8 to 1.0  = ADEQUATE
        < 0.8       = WEAK

    Returns NOT_AVAILABLE when net profit
    is zero or required values are missing.
    """

    if (
        operating_cash_flow is None
        or net_profit is None
    ):
        return CFOQualityResult(
            score=None,
            label=NOT_AVAILABLE
        )

    if net_profit == 0:
        return CFOQualityResult(
            score=None,
            label=NOT_AVAILABLE
        )

    score = (
        operating_cash_flow / net_profit
    )

    if score > 1.0:
        label = STRONG
    elif score >= 0.8:
        label = ADEQUATE
    else:
        label = WEAK

    return CFOQualityResult(
        score=score,
        label=label
    )


def capex_intensity(
    capex,
    sales
):
    """
    Calculate CapEx Intensity.

    Formula:
        CapEx / Sales * 100
    """

    if (
        capex is None
        or sales is None
        or sales == 0
    ):
        return None

    return (
        capex / sales
    ) * 100


def fcf_conversion_rate(
    free_cash_flow_value,
    net_profit
):
    """
    Calculate FCF Conversion Rate.

    Formula:
        FCF / Net Profit * 100
    """

    if (
        free_cash_flow_value is None
        or net_profit is None
        or net_profit == 0
    ):
        return None

    return (
        free_cash_flow_value / net_profit
    ) * 100


def classify_capital_allocation(
    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow
):
    """
    Classify capital allocation using the
    sign pattern of CFO, CFI and CFF.

    Eight possible positive/negative patterns
    are handled.
    """

    if (
        operating_cash_flow is None
        or investing_cash_flow is None
        or financing_cash_flow is None
    ):
        return NOT_AVAILABLE

    cfo_positive = operating_cash_flow >= 0
    cfi_positive = investing_cash_flow >= 0
    cff_positive = financing_cash_flow >= 0

    pattern = (
        cfo_positive,
        cfi_positive,
        cff_positive
    )

    classifications = {
        (
            True,
            False,
            False
        ): "SELF_FUNDED_GROWTH",

        (
            True,
            False,
            True
        ): "EXTERNAL_FUNDED_EXPANSION",

        (
            True,
            True,
            False
        ): "ASSET_SALE_AND_DELEVERAGING",

        (
            True,
            True,
            True
        ): "CASH_ACCUMULATION",

        (
            False,
            False,
            True
        ): "EXTERNAL_FINANCING_DEPENDENT",

        (
            False,
            True,
            True
        ): "ASSET_SALE_AND_EXTERNAL_SUPPORT",

        (
            False,
            True,
            False
        ): "ASSET_SALE_FUNDED_OPERATIONS",

        (
            False,
            False,
            False
        ): "CASH_BURN"
    }

    return classifications[pattern]