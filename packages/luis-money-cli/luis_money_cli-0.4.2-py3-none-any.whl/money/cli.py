import argparse
import sys
from typing import Optional, Sequence

from . import __all__  # noqa: F401 (keep package import happy)
from .accounts import new as accounts_new
from .accounts import list as accounts_list  # noqa: A003 (shadow built-in)
from .income import new as income_new


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="money", description="Money CLI")

    subparsers = parser.add_subparsers(dest="command")

    # money accounts ...
    account_parser = subparsers.add_parser("accounts", help="Manage accounts")
    account_sub = account_parser.add_subparsers(dest="account_cmd")

    # money accounts new <name>
    new_parser = account_sub.add_parser("new", help="Create a new account")
    new_parser.add_argument("name", help="Account name")

    # money accounts list
    account_sub.add_parser("list", help="List all account names")

    # money income ...
    income_parser = subparsers.add_parser("income", help="Manage monthly income")
    income_sub = income_parser.add_subparsers(dest="income_cmd")

    # money income new <MonthName> <ValueInEuros>
    inc_new = income_sub.add_parser(
        "new",
        help="Create or update the income for a given month in the current year",
    )
    inc_new.add_argument(
        "month",
        help="Month name or number (e.g., 'January', 'Jan', '1', '01', 'Nov')",
    )
    inc_new.add_argument(
        "value",
        help="Income value in euros (e.g., 1234.56). Comma separators and '€' allowed.",
    )

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else list(argv))
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "accounts" and args.account_cmd == "new":
        return accounts_new.create(args.name)

    if args.command == "accounts" and args.account_cmd == "list":
        return accounts_list.run()

    if args.command == "income" and args.income_cmd == "new":
        return income_new.create(args.month, args.value)

    # If no valid command provided, show help
    parser.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
