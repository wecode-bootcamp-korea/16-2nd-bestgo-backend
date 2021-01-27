import re

def validate_email(email):
    pattern = re.compile(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return pattern.match(email)

def validate_password(password):
    return re.findall(r'[0-9]',password) and re.findall(r'[a-zA-Z]',password)