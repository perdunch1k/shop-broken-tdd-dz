from shop.money import percent_of

"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def _is_whole_number(value: str) -> bool:
    """True when `int()` would parse `value`.

    The project bans try/except, so the string is judged by shape instead of by
    parsing it: optional sign, optional surrounding spaces, digits only. That is
    what int() tolerates, and anything else must be rejected rather than crash.
    """
    text = value.strip()
    sign = text[:1]
    digits = text[1:] if sign in {"+", "-"} else text
    return digits.isdigit()


def _line_problem(line: dict[str, str]) -> str | None:
    """Return the reason this order line is invalid, or None if it is fine.

    The seven per-line rules live here: the ten rules of validation do not fit in
    one function under the ruff C901 limit of 9.
    """
    for key in REQUIRED_LINE_KEYS:
        if key not in line:
            return f"line: missing key {key}"
    if not line["sku"]:
        return "line: sku must not be empty"
    if not _is_whole_number(line["qty"]):
        return "line: qty is not a whole number"
    if int(line["qty"]) <= 0:
        return "line: qty must be greater than zero"
    if not _is_whole_number(line["unit_price_kopecks"]):
        return "line: unit_price_kopecks is not a whole number"
    if int(line["unit_price_kopecks"]) < 0:
        return "line: unit_price_kopecks must not be negative"
    return None


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "order has no lines"
    seen: list[str] = []
    for line in lines:
        problem = _line_problem(line)
        if problem is not None:
            return problem
        if line["sku"] in seen:
            return f"line: duplicate sku {line['sku']}"
        seen.append(line["sku"])
    if promo_code and promo_code not in PROMO_CODES:
        return f"unknown promo code {promo_code}"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return f"unsupported city {shipping_city}"
    return None


def _tier_discount_percent(units: int) -> int:
    """Percentage of the highest tier whose threshold the order reaches.

    Only one tier applies, so the tiers must not add up. Comparing percentages
    rather than taking the last match keeps this correct whatever order
    TIER_DISCOUNTS is written in.
    """
    best = 0
    for threshold, percent in TIER_DISCOUNTS:
        if units >= threshold and percent > best:
            best = percent
    return best


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None
    subtotal = sum(int(item["qty"]) * int(item["unit_price_kopecks"]) for item in lines)
    units = sum(int(item["qty"]) for item in lines)
    discount = percent_of(subtotal, _tier_discount_percent(units))
    base = subtotal - discount
    return base + percent_of(base, VAT_PERCENT)
