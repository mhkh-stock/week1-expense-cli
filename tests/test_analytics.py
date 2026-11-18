"""Assert-based tests for the Expense CLI analytics and validators.

Run from the project root either way:

    python tests/test_analytics.py     # plain runner, no pytest needed
    python -m pytest tests/            # pytest, if installed

Every test uses plain `assert` statements. A failure prints the test
name and the reason; a pass prints a short summary.
"""

import os
import sys

# Make the src/ package importable from the tests folder.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from analytics import (  # noqa: E402 - sys.path bootstrap above
    add_expense,
    check_budget_status,
    compute_summary_tuple,
    filter_by_category,
    filter_by_date_range,
    get_category_totals,
)
from validators import (  # noqa: E402 - sys.path bootstrap above
    validate_amount,
    validate_category,
    validate_date,
)


def _sample_expenses():
    """Return a small fixed expense list shared by the tests."""
    expenses = []
    add_expense(expenses, "2026-11-10", "Food", 1250.00, "Team lunch")
    add_expense(expenses, "2026-11-11", "Transport", 300.00, "Bus fare")
    add_expense(expenses, "2026-11-12", "Food", 750.00, "Groceries")
    add_expense(expenses, "2026-11-13", "Utilities", 2000.00, "Electricity")
    return expenses


def test_add_expense_stores_record():
    """add_expense appends a dict with the right fields and a unique id."""
    expenses = []
    record = add_expense(expenses, "2026-11-17", "Food", 1250.00,
                         "Team lunch")
    assert len(expenses) == 1
    assert record["id"] == 1
    assert record["date"] == "2026-11-17"
    assert record["category"] == "Food"
    assert record["amount"] == 1250.00
    assert record["description"] == "Team lunch"
    second = add_expense(expenses, "2026-11-18", "Food", 100.00, "Snack")
    assert second["id"] == 2
    assert len(expenses) == 2


def test_category_totals_sum_correctly():
    """get_category_totals adds amounts per category, zero for the rest."""
    totals = get_category_totals(_sample_expenses())
    assert totals["Food"] == 2000.00
    assert totals["Transport"] == 300.00
    assert totals["Utilities"] == 2000.00
    assert totals["Entertainment"] == 0.0
    assert totals["Other"] == 0.0


def test_summary_tuple_values():
    """compute_summary_tuple returns (total, avg, highest, lowest)."""
    total, average, highest, lowest = compute_summary_tuple(
        _sample_expenses())
    assert total == 4300.00
    assert average == 1075.00
    assert highest == 2000.00
    assert lowest == 300.00


def test_summary_tuple_empty_list_is_safe():
    """An empty list returns zeros instead of crashing."""
    assert compute_summary_tuple([]) == (0.0, 0.0, 0.0, 0.0)
    assert get_category_totals([])["Food"] == 0.0
    assert filter_by_category([], "Food") == []


def test_budget_status_safe_below_80_percent():
    """Spending below 80% of the budget is Safe."""
    assert check_budget_status(0.00, 1000.00) == "Safe"
    assert check_budget_status(799.99, 1000.00) == "Safe"


def test_budget_status_warning_at_80_and_100_percent():
    """Spending from 80% to 100% (inclusive) is Warning."""
    assert check_budget_status(800.00, 1000.00) == "Warning"
    assert check_budget_status(950.00, 1000.00) == "Warning"
    assert check_budget_status(1000.00, 1000.00) == "Warning"


def test_budget_status_exceeded_above_100_percent():
    """Spending above 100% of the budget is Exceeded."""
    assert check_budget_status(1000.01, 1000.00) == "Exceeded"
    assert check_budget_status(1500.00, 1000.00) == "Exceeded"


def test_filter_by_category_returns_only_that_category():
    """filter_by_category keeps only matching rows, in order."""
    food = filter_by_category(_sample_expenses(), "Food")
    assert len(food) == 2
    assert all(item["category"] == "Food" for item in food)
    assert food[0]["description"] == "Team lunch"
    assert filter_by_category(_sample_expenses(), "food") == food


def test_filter_by_date_range_is_inclusive():
    """filter_by_date_range keeps both end dates, drops the rest."""
    result = filter_by_date_range(_sample_expenses(),
                                  "2026-11-11", "2026-11-12")
    assert len(result) == 2
    assert result[0]["date"] == "2026-11-11"
    assert result[1]["date"] == "2026-11-12"
    assert filter_by_date_range(_sample_expenses(),
                                "2026-11-10", "2026-11-10") != []


def test_validate_amount_rejects_bad_values():
    """Zero, negative, and non-numeric amounts are rejected."""
    for bad in (0, -50, -0.01, "abc", "", None):
        try:
            validate_amount(bad)
        except ValueError:
            continue
        raise AssertionError("validate_amount accepted: %r" % (bad,))
    assert validate_amount("1250.00") == 1250.00
    assert validate_amount(300) == 300.00


def test_validate_date_rejects_bad_dates():
    """Wrong formats and impossible dates are rejected."""
    for bad in ("17/11/2026", "2026-13-01", "2026-02-30", "Nov 17",
                "2026-11-7", ""):
        try:
            validate_date(bad)
        except ValueError:
            continue
        raise AssertionError("validate_date accepted: %r" % (bad,))
    assert validate_date("2026-11-17") == "2026-11-17"


def test_validate_category_rejects_unknown_and_normalises_case():
    """Unknown categories are rejected; input is case-insensitive."""
    for bad in ("Rent", "Shopping", "", "  "):
        try:
            validate_category(bad)
        except ValueError:
            continue
        raise AssertionError("validate_category accepted: %r" % (bad,))
    assert validate_category("food") == "Food"
    assert validate_category("  TRANSPORT ") == "Transport"


def run_tests():
    """Run every test_ function and print a PASS/FAIL summary."""
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    passed = 0
    for test in tests:
        try:
            test()
        except AssertionError as error:
            print("FAIL: {} — {}".format(test.__name__, error))
        except Exception as error:  # noqa: BLE001 - report any crash
            print("ERROR: {} — {}: {}".format(
                test.__name__, type(error).__name__, error))
        else:
            print("PASS: {}".format(test.__name__))
            passed += 1
    print("\n{} passed, {} failed, {} total.".format(
        passed, len(tests) - passed, len(tests)))
    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
