from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class Money:
    """Value object to handle money amounts in euros.

    - Construct with a single string containing only digits and an optional dot.
      Examples: "0", "12", "2450.75", "." is NOT allowed, "12." is allowed (equals 12.00).
    - Internally stores the value as integer cents to avoid floating point issues.
    - String representation is the euro amount with two decimals (no currency symbol).
    """

    __slots__ = ("_cents",)

    _allowed_re = re.compile(r"^[0-9]*\.?[0-9]*$")

    def __init__(self, value: str):
        if value is None:
            raise ValueError("Value is required")
        s = value.strip()
        if not s:
            raise ValueError("Value is required")

        # Validate allowed characters: digits and at most one dot
        if not self._allowed_re.fullmatch(s):
            raise ValueError("Invalid amount. Use only digits and optional '.' decimal point.")

        # Normalize forms like "." or empty parts
        if s == ".":
            raise ValueError("Invalid amount. Expected digits around decimal point.")
        if s.startswith("."):
            s = "0" + s
        if s.endswith("."):
            s = s + "0"

        try:
            amount = Decimal(s)
        except InvalidOperation as e:
            raise ValueError("Invalid amount format") from e

        self._cents = int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @classmethod
    def from_cents(cls, cents: int) -> Money:
        obj = cls.__new__(cls)
        obj._cents = int(cents)
        return obj

    @property
    def cents(self) -> int:
        return self._cents

    def __int__(self) -> int:  # pragma: no cover - trivial
        return self._cents

    def __str__(self) -> str:
        euros = Decimal(self._cents) / Decimal(100)
        return f"{euros:.2f}"
