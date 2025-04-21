from datetime import datetime
from server.database import get_all_loans, update_loan_status


def update_database_status():
    today_date = datetime.today().date()
    loan_data = get_all_loans()

    for loan in loan_data:
        return_date = loan[4]
        formated_return_date = datetime.strptime(return_date, "%d.%m.%Y").date()
        days_remaining = (formated_return_date - today_date).days
        if days_remaining > 3:
            update_loan_status("green", loan[0])
        elif 0 < days_remaining <= 3:
            update_loan_status("yellow", loan[0])
        elif days_remaining == 0:
            update_loan_status("orange", loan[0])
        elif days_remaining < 0:
            update_loan_status("red", loan[0])
        else:
            print("error")


if __name__ == '__main__':
    update_database_status()