import os
import sqlite3
import sys
import importlib
from datetime import datetime
from pathlib import Path

# Ensure the project root (containing the 'money' package) is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_storage_with_home(tmp_path, monkeypatch):
    """Load money.storage with MONEY_HOME pointing to tmp_path.

    Because money.storage computes DB_PATH at import time, we must
    set the environment and reload the module for each isolated test.
    """
    monkeypatch.setenv("MONEY_HOME", str(tmp_path))
    # Ensure a clean import so APP_DIR/DB_PATH reflect the env override
    if "money.storage" in sys.modules:
        del sys.modules["money.storage"]
    if "money" in sys.modules:
        # Keep the package, but ensure submodule gets re-imported
        pass
    storage = importlib.import_module("money.storage")
    return storage


def test_create_account_success(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    acct = storage.create_account("Savings")

    # Basic structure assertions
    assert set(acct.keys()) == {"id", "name", "created_at"}
    assert isinstance(acct["id"], int) and acct["id"] >= 1
    assert acct["name"] == "Savings"
    assert acct["created_at"].endswith("Z")

    # Check timestamp format up to seconds: YYYY-MM-DDTHH:MM:SSZ
    ts = acct["created_at"].rstrip("Z")
    # Raises ValueError if format is wrong
    datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

    # Verify data persisted in the SQLite DB under MONEY_HOME
    db_file = tmp_path / "money.db"
    assert db_file.exists()
    with sqlite3.connect(db_file) as conn:
        row = conn.execute(
            "SELECT id, name, created_at FROM accounts WHERE id=?", (acct["id"],)
        ).fetchone()
        assert row is not None
        rid, rname, rcreated = row
        assert rid == acct["id"]
        assert rname == "Savings"
        assert rcreated == acct["created_at"]


def test_create_account_empty_name_raises(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    for bad in ["", "   ", None]:
        try:
            storage.create_account(bad)  # type: ignore[arg-type]
            assert False, "Expected ValueError for invalid name"
        except ValueError as e:
            assert "cannot be empty" in str(e).lower()


def test_create_account_duplicate_raises(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    storage.create_account("Wallet")
    try:
        storage.create_account("Wallet")
        assert False, "Expected ValueError on duplicate account name"
    except ValueError as e:
        msg = str(e)
        assert "already exists" in msg.lower()
        assert "wallet" in msg.lower()
