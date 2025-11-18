import sys
import calendar
from decimal import Decimal, ROUND_HALF_UP

from money import storage
from money.month import Month
from money.money import Money


def run(month: str, year: int) -> int:
    """Handle `money savings quantity <MonthName> <Year>`.

    Prints 20 percent of the total income for the given month and year.
    Output is a plain number in euros with two decimals (no currency symbol).
    """
    try:
        m = int(Month(month))
        y = int(year)
        rec = storage.get_month_income(y, m)
        if rec is None:
            month_name = calendar.month_name[m]
            print(
                f"Error: No income found for {y}-{month_name}. Set it with 'money income new {month_name} {y} <value>'.",
                file=sys.stderr,
            )
            return 1

        amount_cents = int(rec["amount_cents"])  # total income in cents
        savings_cents = int(
            (Decimal(amount_cents) * Decimal("0.20")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
        # Format using Money value object
        print(str(Money.from_cents(savings_cents)))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
