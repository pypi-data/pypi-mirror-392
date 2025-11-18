import sys
import re
import calendar
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .. import storage


def _parse_month(month_str: str) -> int:
    """Parse a month representation into an integer 1..12.

    Accepts:
    - Numeric: "1", "01", "12"
    - Names: "January", "Jan" (case-insensitive)
    """
    s = (month_str or "").strip()
    if not s:
        raise ValueError("Month is required")

    # Numeric?
    if re.fullmatch(r"0*[1-9]|1[0-2]", s):
        m = int(s)
        if 1 <= m <= 12:
            return m

    # Name/abbr
    s_lower = s.lower()
    for m in range(1, 13):
        if calendar.month_name[m].lower() == s_lower:
            return m
        if calendar.month_abbr[m].lower() == s_lower:
            return m

    raise ValueError(
        "Invalid month. Use 1-12 or names like 'January'/'Jan'."
    )


def _parse_euros_to_cents(value_str: str) -> int:
    """Parse a human euro value (e.g., "1,234.56", "€1000") to integer cents.

    Rules:
    - Allows optional thousands separators (comma or space)
    - Allows euro sign prefix/suffix
    - Uses dot as decimal separator; also accepts comma as decimal separator if no thousands commas
    - Rounds half up to cents
    """
    if value_str is None:
        raise ValueError("Value is required")
    s = value_str.strip()
    if not s:
        raise ValueError("Value is required")

    # Remove euro sign and spaces around
    s = s.replace("€", "").strip()

    # If it contains exactly one comma and no dot, treat comma as decimal sep
    if "," in s and "." not in s:
        s = s.replace(".", "")  # just in case
        s = s.replace(",", ".")
    else:
        # Remove common thousands separators: comma or space or underscore
        s = re.sub(r"[,_\s]", "", s)

    try:
        amount = Decimal(s)
    except InvalidOperation as e:
        raise ValueError("Invalid euro amount") from e

    cents = int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return cents


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
