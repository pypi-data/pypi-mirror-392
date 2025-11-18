import sys
import calendar

from money import storage
from money.month import Month


def run(month: str, year: int) -> int:
    """Handle `money income delete <MonthName> <Year>`.

    Deletes the income for the specified month and year if it exists.
    """
    try:
        m = int(Month(month))
        y = int(year)
        month_name = calendar.month_name[m]

        rec = storage.get_month_income(y, m)
        if not rec:
            print(
                f"Error: No income found for {y}-{month_name}. Nothing to delete.",
                file=sys.stderr,
            )
            return 1

        deleted = storage.delete_month_income(y, m)
        if deleted:
            print(f"Income deleted: {y}-{month_name}")
            return 0

        # Fallback (shouldn't normally happen):
        print(
            f"Error: No income found for {y}-{month_name}. Nothing to delete.",
            file=sys.stderr,
        )
        return 1

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
