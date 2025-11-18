import os
import sqlite3
import sys
import importlib
from datetime import datetime
from pathlib import Path


# Ensure the project root (which contains the 'money' package) is on sys.path
# __file__ = .../money/repositories/test_storage.py
# parents[0]=.../money/repositories, [1]=.../money, [2]=<project_root>
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_storage_with_home(tmp_path, monkeypatch):
    """Load money.repositories.storage with HOME pointing to tmp_path.

    money.repositories.storage computes its DB_PATH at import time using
    Path.home()/.money, so we set HOME and reload the module for each
    isolated test.
    """
    # Point HOME to a temp directory so ~/.money resolves under tmp_path
    monkeypatch.setenv("HOME", str(tmp_path))
    # On Windows, Path.home may consult USERPROFILE; set it too for robustness
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    # Ensure a clean import so APP_DIR/DB_PATH reflect the env override
    importlib.invalidate_caches()
    if "money.repositories.storage" in sys.modules:
        del sys.modules["money.repositories.storage"]
    storage = importlib.import_module("money.repositories.storage")
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

    # Verify data persisted in the SQLite DB under ~/.money
    db_file = tmp_path / ".money" / "money.db"
    assert db_file.exists()
    with sqlite3.connect(db_file) as conn:
        row = conn.execute(
            "SELECT id, name, created_at FROM accounts WHERE id= ?",
            (acct["id"],),
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


def test_list_accounts_empty(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    assert storage.list_accounts() == []


def test_create_multiple_accounts_and_list_sorted(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    storage.create_account("b")
    storage.create_account("A")
    storage.create_account("c")

    names = storage.list_accounts()
    assert names == ["A", "b", "c"]


def test_create_account_trims_whitespace(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    acct = storage.create_account("   Foo   ")
    assert acct["name"] == "Foo"

    # Ensure it persisted trimmed
    names = storage.list_accounts()
    assert names == ["Foo"]


def test_create_account_case_sensitive_uniqueness(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    storage.create_account("Wallet")
    # Different case should be allowed (SQLite default UNIQUE is case-sensitive)
    storage.create_account("WALLET")

    assert sorted(storage.list_accounts()) == ["WALLET", "Wallet"]


def test_set_month_income_insert_then_accumulate(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    r1 = storage.set_month_income(2024, 1, 100)
    assert set(r1.keys()) == {"id", "year", "month", "amount_cents", "updated_at"}
    assert r1["year"] == 2024 and r1["month"] == 1 and r1["amount_cents"] == 100
    assert r1["updated_at"].endswith("Z")
    datetime.strptime(r1["updated_at"].rstrip("Z"), "%Y-%m-%dT%H:%M:%S")

    r2 = storage.set_month_income(2024, 1, 50)
    assert r2["amount_cents"] == 150

    # get should reflect the accumulated total
    got = storage.get_month_income(2024, 1)
    assert got is not None
    assert got["amount_cents"] == 150


def test_set_month_income_invalid_month_raises(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    for bad in [0, 13, -1, 100]:
        try:
            storage.set_month_income(2024, bad, 10)
            assert False, "Expected ValueError for invalid month"
        except ValueError as e:
            assert "month must be in 1..12" in str(e).lower()


def test_get_month_income_none_when_missing(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    assert storage.get_month_income(2030, 5) is None


def test_list_incomes_ordered_by_year_month(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    storage.set_month_income(2023, 12, 100)
    storage.set_month_income(2023, 5, 50)
    storage.set_month_income(2022, 6, 30)
    storage.set_month_income(2024, 1, 10)

    rows = storage.list_incomes()
    ym = [(r["year"], r["month"]) for r in rows]
    assert ym == [(2022, 6), (2023, 5), (2023, 12), (2024, 1)]


def test_delete_month_income_effect_and_return_value(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    storage.set_month_income(2024, 2, 40)
    assert storage.get_month_income(2024, 2) is not None

    deleted = storage.delete_month_income(2024, 2)
    assert deleted == 1
    assert storage.get_month_income(2024, 2) is None

    # Deleting again should return 0
    deleted_again = storage.delete_month_income(2024, 2)
    assert deleted_again == 0


def test_set_month_income_timestamp_format(tmp_path, monkeypatch):
    storage = _load_storage_with_home(tmp_path, monkeypatch)

    r = storage.set_month_income(2025, 11, 1)
    ts = r["updated_at"]
    assert ts.endswith("Z")
    datetime.strptime(ts.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
