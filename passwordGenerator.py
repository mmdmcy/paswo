import random
import string

def generatePasswordString(specialChars, useUppercase, length, exclude_similar=False, exclude_chars="", require_2_upper=True, require_2_digits=True, require_2_special=True):
    """
    Generates a random password string with specified complexity.
    """
    
    # Define character sets
    lower_case = string.ascii_lowercase
    upper_case = string.ascii_uppercase
    digits = string.digits
    
    if exclude_similar:
        similar_chars = "Il1O0"
        lower_case = ''.join(c for c in lower_case if c not in similar_chars)
        upper_case = ''.join(c for c in upper_case if c not in similar_chars)
        digits = ''.join(c for c in digits if c not in similar_chars)

    if exclude_chars:
        lower_case = ''.join(c for c in lower_case if c not in exclude_chars)
        upper_case = ''.join(c for c in upper_case if c not in exclude_chars)
        digits = ''.join(c for c in digits if c not in exclude_chars)
        specialChars = ''.join(c for c in specialChars if c not in exclude_chars)

    # Base character set
    characters = lower_case
    if useUppercase:
        characters += upper_case
    characters += digits
    characters += specialChars
    
    if not characters:
        return "Error: No characters available"
        
    password_list = []
    guaranteed_chars = []

    # Enforce complexity rules
    if require_2_upper and useUppercase and len(upper_case) >= 2:
        guaranteed_chars.extend(random.sample(upper_case, 2))
    if require_2_digits and len(digits) >= 2:
        guaranteed_chars.extend(random.sample(digits, 2))
    if require_2_special and len(specialChars) >= 2:
        guaranteed_chars.extend(random.sample(specialChars, 2))

    # Fill the rest of the password length
    remaining_length = length - len(guaranteed_chars)
    if remaining_length > 0:
        password_list.extend(random.choices(characters, k=remaining_length))
    
    password_list.extend(guaranteed_chars)
    
    # Shuffle the final password list to ensure randomness
    random.shuffle(password_list)
    
    return "".join(password_list)
