"""Expense storage, budget checks and summary metrics.

All functions take their data as explicit parameters and return plain
values (lists, dicts, tuples, strings). There is no module-level mutable
state: the CLI owns the expense list and the budgets dict and passes
them in on every call.
"""

from validators import (
    VALID_CATEGORIES,
    validate_amount,
    validate_category,
    validate_date,
)


def add_expense(expenses, date, category, amount, description=""):
    """Validate the fields, append a new expense dict, and return it.

    The id is one more than the highest id already in the list (1 when
    the list is empty), so ids stay unique even after filtering.
    """
    clean_date = validate_date(date)
    clean_category = validate_category(category)
    clean_amount = validate_amount(amount)
    clean_description = str(description).strip()
    next_id = max((item["id"] for item in expenses), default=0) + 1
    record = {
        "id": next_id,
        "date": clean_date,
        "category": clean_category,
        "amount": clean_amount,
        "description": clean_description,
    }
    expenses.append(record)
    return record


def filter_by_category(expenses, category):
    """Return the expenses whose category matches (case-insensitive)."""
    clean_category = validate_category(category)
    return [item for item in expenses if item["category"] == clean_category]


def filter_by_date_range(expenses, start_date, end_date):
    """Return expenses with date in [start_date, end_date] (inclusive).

    Both dates are validated as YYYY-MM-DD. Raises ValueError when the
    start date is after the end date.
    """
    start = validate_date(start_date)
    end = validate_date(end_date)
    if start > end:
        raise ValueError("Start date must not be after the end date.")
    return [item for item in expenses if start <= item["date"] <= end]


def get_category_totals(expenses):
    """Return {category: total spent} for every valid category.

    Categories with no expenses report 0.0, so the report always shows
    the full set and percentages always add up.
    """
    totals = {category: 0.0 for category in VALID_CATEGORIES}
    for item in expenses:
        totals[item["category"]] += item["amount"]
    return totals


def get_category_percentages(expenses):
    """Return {category: share of total spend in percent}.

    An empty expense list gives 0.0 for every category, so there is no
    division by zero.
    """
    totals = get_category_totals(expenses)
    total = sum(totals.values())
    if total == 0:
        return {category: 0.0 for category in VALID_CATEGORIES}
    return {
        category: (amount / total) * 100.0
        for category, amount in totals.items()
    }


def check_budget_status(spent, budget):
    """Return Safe / Warning / Exceeded for one category budget.

    Safe is below 80% of the budget, Warning is 80% to 100%
    (inclusive), Exceeded is above 100%. Raises ValueError for a
    zero or negative budget, or a negative spent amount.
    """
    clean_budget = validate_amount(budget)
    try:
        spent_amount = float(spent)
    except (TypeError, ValueError):
        raise ValueError("Spent amount must be a number.") from None
    if spent_amount < 0:
        raise ValueError("Spent amount cannot be negative.")
    ratio = spent_amount / clean_budget
    if ratio < 0.80:
        return "Safe"
    if ratio <= 1.00:
        return "Warning"
    return "Exceeded"


def set_budget(budgets, category, amount):
    """Validate and store a monthly budget cap; return the budgets dict."""
    clean_category = validate_category(category)
    clean_amount = validate_amount(amount)
    budgets[clean_category] = clean_amount
    return budgets


def compute_summary_tuple(expenses):
    """Return (total, average, highest, lowest) expense amounts.

    An empty list returns (0.0, 0.0, 0.0, 0.0) instead of crashing,
    so the analytics report is safe to run before any expense is added.
    """
    if not expenses:
        return (0.0, 0.0, 0.0, 0.0)
    amounts = [item["amount"] for item in expenses]
    total = sum(amounts)
    average = total / len(amounts)
    return (total, average, max(amounts), min(amounts))
