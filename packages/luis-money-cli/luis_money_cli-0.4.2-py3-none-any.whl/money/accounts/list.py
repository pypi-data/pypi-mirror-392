from .. import storage


def run() -> int:
    """Handle `money accounts list` command.

    Prints one account name per line. Returns 0.
    """
    names = storage.list_accounts()
    for name in names:
        print(name)
    return 0
