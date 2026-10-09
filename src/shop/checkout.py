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


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if lines[0] is None or lines[0]["sku"] is None:
        return "1"
    if not (all(x for x in lines[0] if x in REQUIRED_LINE_KEYS)):
        return "2"
    if int(lines[0]["qty"]) % 1 == int(lines[0]["qty"]) or int(lines[0]["qty"]) <= 0:
        return "3"
    if type(int(lines[0]["unit_price_kopecks"])) is not int:
        return "4"
    if int(lines[0]["unit_price_kopecks"]) < 0:
        return "5"
    if len(lines) > 1 and lines[0]["sku"] == lines[1]["sku"]:
        return "6"
    if promo_code != "" and promo_code not in PROMO_CODES:
        return "7"
    if shipping_city != "" and shipping_city not in SUPPORTED_CITIES:
        return "8"
    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is None:
        subtotal = int(lines[0]["qty"]) * int(lines[0]["unit_price_kopecks"])
        max_tier_disc = 0
        for i in range(len(TIER_DISCOUNTS)):
            if int(lines[0]["qty"]) >= TIER_DISCOUNTS[i][0]:
                max_tier_disc = TIER_DISCOUNTS[i][1]
        promo_discount = PROMO_CODES[promo_code] if promo_code != "" else 0
        discount_percent = max(max_tier_disc, promo_discount)
        if discount_percent > MAX_DISCOUNT_PERCENT:
            discount_percent = MAX_DISCOUNT_PERCENT
        discount = percent_of(subtotal, discount_percent)
        discounted_subtotal = subtotal - discount
        if (
            shipping_city is not None
            and shipping_city != ""
            and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS
        ):
            shipping_cost = SHIPPING_KOPEKS
        else:
            shipping_cost = 0
        base = discounted_subtotal + shipping_cost
        vat = percent_of(base, VAT_PERCENT)
        return base + vat
    return None
