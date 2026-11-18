"""Interactive CLI menu for the Personal Expense & Budget Analyzer.

Run from the project root:

    python src/main.py

Menu:
    1. Add Expense
    2. View All Expenses
    3. Filter Expenses (by Category / Date Range)
    4. Set Monthly Budget
    5. Analytics Report
    6. Exit

All data lives in memory for the session. Invalid input is caught and
re-prompted; the program never crashes on bad text, negative numbers,
or an empty expense list.
"""

from analytics import (
    VALID_CATEGORIES,
    add_expense,
    check_budget_status,
    compute_summary_tuple,
    filter_by_category,
    filter_by_date_range,
    get_category_percentages,
    get_category_totals,
    set_budget,
)
from validators import validate_amount, validate_category, validate_date


def read_line(prompt):
    """Read one line of input; return None on EOF (Ctrl+D / end of pipe)."""
    try:
        return input(prompt)
    except EOFError:
        return None


def prompt_amount(prompt):
    """Ask for a positive amount until a valid one is given."""
    while True:
        raw = read_line(prompt)
        if raw is None:
            return None
        try:
            return validate_amount(raw.strip())
        except ValueError as error:
            print("  ! " + str(error) + " Try again.")


def prompt_date(prompt):
    """Ask for a date in YYYY-MM-DD until a valid one is given."""
    while True:
        raw = read_line(prompt)
        if raw is None:
            return None
        try:
            return validate_date(raw)
        except ValueError as error:
            print("  ! " + str(error) + " Try again.")


def prompt_category(prompt):
    """Ask for a category until a valid one is given."""
    valid = ", ".join(sorted(VALID_CATEGORIES))
    while True:
        raw = read_line(prompt + " (" + valid + "): ")
        if raw is None:
            return None
        try:
            return validate_category(raw)
        except ValueError as error:
            print("  ! " + str(error) + " Try again.")


def print_expense_table(expenses):
    """Print expenses as an aligned table, or an empty-state message."""
    if not expenses:
        print("\nNo expenses to show yet. Add one from option 1.")
        return
    print()
    print("{:<5} {:<12} {:<14} {:>12}  {}".format(
        "ID", "Date", "Category", "Amount", "Description"))
    print("-" * 70)
    for item in expenses:
        print("{:<5} {:<12} {:<14} {:>12.2f}  {}".format(
            item["id"], item["date"], item["category"],
            item["amount"], item["description"]))
    print("-" * 70)
    print("Total: {:.2f}  ({} expense{})".format(
        sum(item["amount"] for item in expenses),
        len(expenses), "" if len(expenses) == 1 else "s"))


def print_budget_report(expenses, budgets):
    """Print spent vs budget per category with Safe/Warning/Exceeded tags."""
    totals = get_category_totals(expenses)
    print()
    print("Monthly Budget Status")
    print("-" * 70)
    if not budgets:
        print("No budgets set yet. Use option 4 to set a monthly cap.")
        return
    print("{:<14} {:>12} {:>12} {:>8}  {}".format(
        "Category", "Spent", "Budget", "Used", "Status"))
    print("-" * 70)
    for category in sorted(budgets):
        spent = totals[category]
        budget = budgets[category]
        used = (spent / budget) * 100.0 if budget else 0.0
        status = check_budget_status(spent, budget)
        print("{:<14} {:>12.2f} {:>12.2f} {:>7.1f}%  {}".format(
            category, spent, budget, used, status))


def print_analytics(expenses, budgets):
    """Print the summary tuple, category shares, and budget status."""
    total, average, highest, lowest = compute_summary_tuple(expenses)
    totals = get_category_totals(expenses)
    shares = get_category_percentages(expenses)
    print()
    print("Analytics Report")
    print("-" * 70)
    print("Total spend:      {:.2f}".format(total))
    print("Average expense:  {:.2f}".format(average))
    print("Highest expense:  {:.2f}".format(highest))
    print("Lowest expense:   {:.2f}".format(lowest))
    print("Number of items:  {}".format(len(expenses)))
    print()
    print("Spending by category")
    print("{:<14} {:>12} {:>8}".format("Category", "Amount", "Share"))
    print("-" * 70)
    for category in sorted(totals):
        print("{:<14} {:>12.2f} {:>7.1f}%".format(
            category, totals[category], shares[category]))
    if budgets:
        print_budget_report(expenses, budgets)


def add_expense_flow(expenses):
    """Guide the user through adding one expense."""
    print("\nAdd Expense")
    date = prompt_date("Date (YYYY-MM-DD): ")
    if date is None:
        return
    category = prompt_category("Category")
    if category is None:
        return
    amount = prompt_amount("Amount: ")
    if amount is None:
        return
    description = read_line("Description: ")
    if description is None:
        return
    record = add_expense(expenses, date, category, amount, description)
    print("\nAdded expense #{}: {} | {} | {:.2f} | {}".format(
        record["id"], record["date"], record["category"],
        record["amount"], record["description"]))


def filter_flow(expenses):
    """Filter by category, by date range, or by both, then show matches."""
    print("\nFilter Expenses")
    print("  1. By category")
    print("  2. By date range")
    print("  3. By category AND date range")
    print("  0. Back to main menu")
    choice = read_line("Choose (0-3): ")
    if choice is None:
        return
    choice = choice.strip()
    if choice == "0":
        return
    if choice not in ("1", "2", "3"):
        print("  ! Please choose 0, 1, 2 or 3.")
        return
    results = expenses
    if choice in ("1", "3"):
        category = prompt_category("Category")
        if category is None:
            return
        results = filter_by_category(results, category)
    if choice in ("2", "3"):
        start = prompt_date("Start date (YYYY-MM-DD): ")
        if start is None:
            return
        end = prompt_date("End date (YYYY-MM-DD): ")
        if end is None:
            return
        try:
            results = filter_by_date_range(results, start, end)
        except ValueError as error:
            print("  ! " + str(error))
            return
    print_expense_table(results)


def set_budget_flow(budgets):
    """Set a monthly budget cap for one category."""
    print("\nSet Monthly Budget")
    category = prompt_category("Category")
    if category is None:
        return
    amount = prompt_amount("Monthly budget cap: ")
    if amount is None:
        return
    set_budget(budgets, category, amount)
    print("\nBudget set: {} = {:.2f} per month.".format(category, amount))


def show_menu():
    """Print the main menu."""
    print()
    print("=" * 50)
    print("  Personal Expense & Budget CLI Analyzer")
    print("=" * 50)
    print("  1. Add Expense")
    print("  2. View All Expenses")
    print("  3. Filter Expenses (by Category / Date Range)")
    print("  4. Set Monthly Budget")
    print("  5. Analytics Report")
    print("  6. Exit")
    print("-" * 50)


def main():
    """Run the menu loop until the user chooses Exit."""
    expenses = []
    budgets = {}
    print("Welcome! Your expenses are kept in memory for this session.")
    while True:
        show_menu()
        raw = read_line("Choose an option (1-6): ")
        if raw is None:
            print("\nGoodbye! (input ended)")
            return
        choice = raw.strip()
        if choice == "1":
            add_expense_flow(expenses)
        elif choice == "2":
            print_expense_table(expenses)
        elif choice == "3":
            filter_flow(expenses)
        elif choice == "4":
            set_budget_flow(budgets)
        elif choice == "5":
            print_analytics(expenses, budgets)
        elif choice == "6":
            print("\nGoodbye! Thanks for using the Expense Analyzer.")
            return
        else:
            print("  ! Please choose a number from 1 to 6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye! (interrupted)")
