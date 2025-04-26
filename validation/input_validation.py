import re

def validate_string(input_value, field_name, min_length=1, max_length=None):
    if not isinstance(input_value, str):
        return False, f"{field_name} must be a string."
    
    input_value = input_value.strip()
    length = len(input_value)
    
    if length == 0:  # Explicitly handle empty values
        return False, f"{field_name} cannot be empty."

    if length < min_length:
        return False, f"{field_name} must be at least {min_length} characters long."
       
    if max_length and length > max_length:
        return False, f"{field_name} must be no longer than {max_length} characters."

    # Updated regex pattern to accept letters, digits, spaces, periods, comma and apostrophes
    pattern = r"^(?![\s.,']+$)[a-zA-Z0-9\s.,']+$"

    if not re.match(pattern, input_value):
        return False, f"{field_name} contains invalid characters."

    return True, None