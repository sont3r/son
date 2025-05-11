import re


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password strength
    - At least 8 characters
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False

    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return False

    # Check for at least one special character
    special_chars = '!@#$%^&*()-_=+[]{}|;:,.<>?/`~'
    if not any(char in special_chars for char in password):
        return False

    return True


def format_time(time_obj):
    """Format time object to HH:MM string"""
    if time_obj:
        return time_obj.strftime('%H:%M')
    return None


def format_date(date_obj):
    """Format date object to YYYY-MM-DD string"""
    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    return None
