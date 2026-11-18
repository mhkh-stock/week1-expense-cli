"""Input validation helpers for the Expense CLI.

Each validator either returns a clean value or raises ValueError with a
plain message the CLI can show and re-prompt on. Nothing here touches
the terminal; the CLI decides how to present the error.
"""

from datetime import datetime
import re

# Valid categories, kept in a set for O(1) lookup.
VALID_CATEGORIES = {"Food", "Transport", "Utilities", "Entertainment",
                    "Other"}

DATE_FORMAT = "%Y-%m-%d"
# Strict shape: exactly 4 digits, dash, 2 digits, dash, 2 digits.
# strptime alone is lenient (it accepts "2026-11-7"), so the shape is
# checked first and strptime then confirms it is a real calendar date.
DATE_SHAPE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_amount(value):
    """Return value as a float when it is a positive number.

    Accepts a string or a number. Raises ValueError for text that is
    not a number, and for zero or negative amounts.
    """
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a number, e.g. 1250.00.") from None
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return amount


def validate_date(date_str):
    """Return the date string when it is a real date in YYYY-MM-DD form.

    Uses strict parsing, so 2026-02-30 or 17/11/2026 are rejected.
    Raises ValueError otherwise.
    """
    if not isinstance(date_str, str):
        raise ValueError("Date must be text in YYYY-MM-DD form.")
    text = date_str.strip()
    if not DATE_SHAPE.match(text):
        raise ValueError(
            "Date must be a real date in YYYY-MM-DD form, "
            "e.g. 2026-11-17."
        )
    try:
        parsed = datetime.strptime(text, DATE_FORMAT)
    except ValueError:
        raise ValueError(
            "Date must be a real date in YYYY-MM-DD form, "
            "e.g. 2026-11-17."
        ) from None
    return parsed.strftime(DATE_FORMAT)


def validate_category(category):
    """Return the category in title case when it is one of the valid ones.

    Input is case-insensitive ("food" becomes "Food"). Raises
    ValueError with the list of valid categories otherwise.
    """
    if not isinstance(category, str):
        raise ValueError("Category must be text.")
    cleaned = category.strip().title()
    if cleaned not in VALID_CATEGORIES:
        valid = ", ".join(sorted(VALID_CATEGORIES))
        raise ValueError("Category must be one of: " + valid + ".")
    return cleaned
