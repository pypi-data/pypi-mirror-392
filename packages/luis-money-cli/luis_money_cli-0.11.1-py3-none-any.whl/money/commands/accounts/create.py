import sys

from money.repositories import storage


def create(name: str) -> int:
    """Create a new account by name.

    Handles the `money accounts new <name>` command.
    Returns POSIX-style exit code.
    """
    try:
        acct = storage.create_account(name)
        print(
            f"Account created: {acct['name']} (id={acct['id']}, created_at={acct['created_at']})"
        )
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
