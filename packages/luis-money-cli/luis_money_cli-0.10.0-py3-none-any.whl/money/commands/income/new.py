import sys
import calendar
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from money import storage
from money.month import Month
from money.money import Money


def _parse_month(month_str: str) -> int:
    """Parse a month string accepting only full names (case-insensitive).

    Example inputs: "January", "february".
    """
    return int(Month(month_str))


def _parse_euros_to_cents(value_str: str) -> int:
    """Parse a euro value allowing only digits and an optional '.' as decimal separator."""
    return Money(value_str).cents


def create(month: str, year: int, value: str) -> int:
    """Handle `money income new <MonthName> <Year> <ValueInEuros>`.

    Saves/updates the income for the specified month and year.
    """
    try:
        m = _parse_month(month)
        y = int(year)
        amount_cents = _parse_euros_to_cents(value)
        rec = storage.set_month_income(y, m, amount_cents)

        # Pretty print
        month_name = calendar.month_name[m]
        euros = Decimal(rec["amount_cents"]) / Decimal(100)
        print(
            f"Income set: {y}-{month_name} -> €{euros:.2f} (id={rec['id']}, updated_at={rec['updated_at']})"
        )
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
