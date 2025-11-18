# Money CLI — Examples

This project provides a minimal CLI to manage accounts, monthly income, and a simple savings calculation. Below are quick examples — one per command — to help you get started.

Assuming the tool is installed (entrypoint `money`), run the commands from your shell.

## Commands and Examples

1) Create a new account

```
money accounts new "Checking"
```

2) List all accounts

```
money accounts list
```

3) Create or update monthly income

```
money income new November 2025 2450.75
```

4) Show savings quantity (20% of total income) for a given month

```
money savings quantity November 2025
```

Notes:
- Month must be the full month name (case-insensitive), e.g., `January`, `november`.
- Income value must contain only digits and an optional `.` as decimal point (e.g., `1234.56`, `2450.75`). Commas, spaces, and currency symbols are not allowed.
- Exit codes follow POSIX conventions (`0` for success; non-zero indicates an error).
