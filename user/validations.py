from django.contrib.auth import get_user_model
import re
from datetime import datetime

User = get_user_model()

def validate_credentials(email, password, dob, check_email=False):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # checks for a valid email address format
        return False, "Invalid Email Address"
    if check_email:
        if User.objects.filter(email=email).exists():
            return False, "Email already registered!"
    if len(password) < 7:
        return False, "Password must be at least 7 characters long"
    if not re.search(r"\d", password) or not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one number and one uppercase letter"
    try:
        if dob > datetime.now().date(): # dob can't be in the future
            return False, "Are you from future? Enter correct birth date"
    except Exception as e:
        return False, "Enter correct birth date"
    return True, ""