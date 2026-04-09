from decimal import Decimal, InvalidOperation


def change_currency_from_vnd(amount, to_currency):
    exchange_rates = {
        "USD": Decimal("1"),
        "VND": Decimal("25000"),
    }

    if to_currency not in exchange_rates:
        raise ValueError("Unsupported currency")

    try:
        amount_decimal = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        raise ValueError("Invalid amount")

    converted_amount = (
        amount_decimal / exchange_rates["VND"] * exchange_rates[to_currency]
    )
    return converted_amount
