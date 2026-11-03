class Equipment:
    def __init__(self, asset_code, name, category, location, condition, status="Available", asset_id=None):
        self.asset_id = asset_id
        self.asset_code = asset_code
        self.name = name
        self.category = category
        self.location = location
        self.condition = condition
        self.status = status

class Borrower:
    def __init__(self, borrower_code, display_name, department_or_program, active=1, borrower_id=None):
        self.borrower_id = borrower_id
        self.borrower_code = borrower_code
        self.display_name = display_name
        self.department_or_program = department_or_program
        self.active = active

class Loan:
    def __init__(self, asset_id, borrower_id, borrowed_on, due_on, returned_on=None, status="Active", loan_id=None):
        self.loan_id = loan_id
        self.asset_id = asset_id
        self.borrower_id = borrower_id
        self.borrowed_on = borrowed_on
        self.due_on = due_on
        self.returned_on = returned_on
        self.status = status
