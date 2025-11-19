import calendar


class Month:
    """Value object representing a calendar month (1..12).

    Accepts only full month names (case-insensitive), e.g., "January", "february".
    Provides helpers to convert to int and string.
    """

    __slots__ = ("_n",)

    _name_to_num = {calendar.month_name[i].lower(): i for i in range(1, 13)}

    def __init__(self, month_name: str):
        """Create from a full month name (case-insensitive).

        Examples: "January", "february". Abbreviations like "Jan" or numbers like "1"
        are NOT accepted.
        """
        s = (month_name or "").strip()
        if not s:
            raise ValueError("Month is required")
        n = self._name_to_num.get(s.lower())
        if not n:
            raise ValueError("Invalid month. Use full month names like 'January'.")
        self._n = int(n)

    @property
    def number(self) -> int:
        return self._n

    @property
    def name(self) -> str:
        return calendar.month_name[self._n]

    def __int__(self) -> int:  # pragma: no cover - trivial
        return self._n

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name
