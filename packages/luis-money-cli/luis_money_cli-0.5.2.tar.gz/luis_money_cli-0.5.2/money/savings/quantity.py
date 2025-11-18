import sys
import calendar
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from .. import storage
from ..income.new import _parse_month


def run(month: str) -> int:
    """Handle `money savings quantity <MonthName>`.

    Prints 20% of the total income for the given month (current year).
    Output is a plain number in euros with two decimals (no currency symbol).
    """
    try:
        m = _parse_month(month)
        year = datetime.now().year
        rec = storage.get_month_income(year, m)
        if rec is None:
            month_name = calendar.month_name[m]
            print(
                f"Error: No income found for {year}-{month_name}. Set it with 'money income new {month_name} <value>'.",
                file=sys.stderr,
            )
            return 1

        amount_cents = int(rec["amount_cents"])  # total income in cents
        savings_cents = int(
            (Decimal(amount_cents) * Decimal("0.20")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
        euros = Decimal(savings_cents) / Decimal(100)
        # Print as plain number with two decimals
        print(f"{euros:.2f}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
