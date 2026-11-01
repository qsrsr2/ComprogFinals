from datetime import datetime

def validate_required_fields(fields_dict):
    """
    Checks if all required fields contain data.
    Expects a dictionary of field_name: field_value.
    Returns (True, "") if valid, or (False, error_message) if invalid.
    """
    for field_name, value in fields_dict.items():
        if value is None:
            return False, f"{field_name} cannot be null."
        elif isinstance(value, str) and not value.strip():
            return False, f"{field_name} cannot be empty."
    return True, "All required fields present."



def validate_date_format(date_text):
    """Validates that a date matches the YYYY-MM-DD format."""
    try:
        valid_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        return True, valid_date
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD."

def validate_checkout_dates(borrow_date_str, due_date_str):
    # Validate borrow date format
    b_success, b_result = validate_date_format(borrow_date_str)
    if not b_success:
        return False, f"Borrow Date Error: {b_result}"
        
    # Validate due date format
    d_success, d_result = validate_date_format(due_date_str)
    if not d_success:
        return False, f"Due Date Error: {d_result}"
        
    # Business rule: due date cannot precede borrow date
    if d_result < b_result:
        return False, "Due date cannot be earlier than the borrow date."
    elif d_result == b_result:
        return True, "Same-day checkout valid."
    else:
        return True, "Dates are valid."