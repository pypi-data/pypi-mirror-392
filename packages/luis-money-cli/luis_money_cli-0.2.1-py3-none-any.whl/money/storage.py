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
