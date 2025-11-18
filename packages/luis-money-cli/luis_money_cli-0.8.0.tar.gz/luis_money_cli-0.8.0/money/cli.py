import argparse
import sys
from typing import Optional, Sequence

from . import __all__  # noqa: F401 (keep package import happy)
from money.commands.accounts import new as accounts_new, list as accounts_list
from money.commands.income import new as income_new
from money.commands.savings import quantity as savings_quantity


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

    # money income new <MonthName> <Year> <ValueInEuros>
    inc_new = income_sub.add_parser(
        "new",
        help="Create or update the income for a given month and year",
    )
    inc_new.add_argument(
        "month",
        help="Full month name only (case-insensitive), e.g., 'January', 'november'",
    )
    inc_new.add_argument(
        "year",
        type=int,
        help="Year (e.g., 2025)",
    )
    inc_new.add_argument(
        "value",
        help="Income value in euros. Only digits and an optional '.' decimal point are allowed (e.g., 1234.56).",
    )

    # money savings ...
    savings_parser = subparsers.add_parser("savings", help="Savings related commands")
    savings_sub = savings_parser.add_subparsers(dest="savings_cmd")

    # money savings quantity <MonthName> <Year>
    sav_qty = savings_sub.add_parser(
        "quantity",
        help="Show 20 percent of the total income for the specified month and year",
    )
    sav_qty.add_argument(
        "month",
        help="Full month name only (case-insensitive), e.g., 'January', 'november'",
    )
    sav_qty.add_argument(
        "year",
        type=int,
        help="Year (e.g., 2025)",
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
        return income_new.create(args.month, args.year, args.value)

    if args.command == "savings" and args.savings_cmd == "quantity":
        return savings_quantity.run(args.month, args.year)

    # If no valid command provided, show help
    parser.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
