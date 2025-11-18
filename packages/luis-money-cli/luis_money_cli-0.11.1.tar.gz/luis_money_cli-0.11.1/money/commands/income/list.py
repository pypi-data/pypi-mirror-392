import calendar
from decimal import Decimal

from money.repositories import storage


def run() -> int:
    """Handle `money income list` command.

    Prints one income per line ordered by year then month.
    Format: YYYY-MonthName -> €X.YY (id=ID, updated_at=TIMESTAMP)
    If there are no incomes, prints nothing and returns 0.
    """
    rows = storage.list_incomes()
    for r in rows:
        month_name = calendar.month_name[int(r["month"])]
        euros = Decimal(int(r["amount_cents"])) / Decimal(100)
        print(
            f"{r['year']}-{month_name} -> €{euros:.2f} (id={r['id']}, updated_at={r['updated_at']})"
        )
    return 0
