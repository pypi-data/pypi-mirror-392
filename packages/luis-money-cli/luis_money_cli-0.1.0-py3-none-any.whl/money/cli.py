import argparse
import sys
from typing import Optional, Sequence

from . import __all__  # noqa: F401 (keep package import happy)
from . import storage


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="money", description="Money CLI")

    subparsers = parser.add_subparsers(dest="command")

    # money account ...
    account_parser = subparsers.add_parser("account", help="Manage accounts")
    account_sub = account_parser.add_subparsers(dest="account_cmd")

    # money account new <name>
    new_parser = account_sub.add_parser("new", help="Create a new account")
    new_parser.add_argument("name", help="Account name")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else list(argv))
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "account" and args.account_cmd == "new":
        try:
            acct = storage.create_account(args.name)
            print(f"Account created: {acct['name']} (id={acct['id']}, created_at={acct['created_at']})")
            return 0
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # If no valid command provided, show help
    parser.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
