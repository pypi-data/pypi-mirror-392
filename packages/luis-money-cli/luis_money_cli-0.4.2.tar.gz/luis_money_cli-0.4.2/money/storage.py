import os
import sqlite3
from datetime import datetime
from pathlib import Path


APP_DIR = Path(os.environ.get("MONEY_HOME", Path.home() / ".money"))
DB_PATH = APP_DIR / "money.db"


def _ensure_db():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
                amount_cents INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(year, month)
            )
            """
        )


def create_account(name: str) -> dict:
    """Create a new account with the given name.

    Returns a dict with keys: id, name, created_at.
    Raises ValueError if the name is invalid or already exists.
    """
    name = (name or "").strip()
    if not name:
        raise ValueError("Account name cannot be empty")

    _ensure_db()
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                "INSERT INTO accounts(name, created_at) VALUES(?, ?)", (name, created_at)
            )
            account_id = cur.lastrowid
            return {"id": account_id, "name": name, "created_at": created_at}
    except sqlite3.IntegrityError as e:
        # Likely UNIQUE constraint failed
        raise ValueError(f"Account '{name}' already exists") from e


def list_accounts() -> list[str]:
    """Return a list of all account names.

    The names are ordered alphabetically (case-insensitive by SQLite default).
    If no accounts exist, returns an empty list.
    """
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT name FROM accounts ORDER BY name ASC").fetchall()
        return [r[0] for r in rows]


def set_month_income(year: int, month: int, amount_cents: int) -> dict:
    """Create or update the income for a given year and month.

    Stores the value in cents to avoid floating point issues.
    Returns a dict with keys: id, year, month, amount_cents, updated_at.
    """
    if not (1 <= int(month) <= 12):
        raise ValueError("Month must be in 1..12")
    year = int(year)
    amount_cents = int(amount_cents)
    _ensure_db()
    updated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    with sqlite3.connect(DB_PATH) as conn:
        # Try update first; if no row updated, insert
        cur = conn.execute(
            "UPDATE incomes SET amount_cents = ?, updated_at = ? WHERE year = ? AND month = ?",
            (amount_cents, updated_at, year, month),
        )
        if cur.rowcount == 0:
            cur = conn.execute(
                "INSERT INTO incomes(year, month, amount_cents, updated_at) VALUES(?, ?, ?, ?)",
                (year, month, amount_cents, updated_at),
            )
            row_id = cur.lastrowid
        else:
            # Fetch the id of the updated row
            row_id = conn.execute(
                "SELECT id FROM incomes WHERE year = ? AND month = ?",
                (year, month),
            ).fetchone()[0]

        return {
            "id": row_id,
            "year": year,
            "month": month,
            "amount_cents": amount_cents,
            "updated_at": updated_at,
        }
