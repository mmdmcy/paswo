import secrets
import string

# os.urandom-backed generator: passwords must not come from the Mersenne Twister
random = secrets.SystemRandom()

def generatePasswordString(specialChars, useUppercase, length, exclude_similar=False, exclude_chars="", minUppercase=0, minDigits=0, minSpecial=0, useDashes=False, dashSpacing=0, requiredText=""):
    """
    generates a random password string with specified complexity.
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

    # base character set
    characters = lower_case
    if useUppercase:
        characters += upper_case
    characters += digits
    characters += specialChars
    
    if not characters:
        return "error: no characters available"
        
    password_list = []
    guaranteed_chars = []

    # enforce complexity rules
    if minUppercase > 0 and useUppercase and len(upper_case) >= minUppercase:
        guaranteed_chars.extend(random.sample(upper_case, minUppercase))
    if minDigits > 0 and len(digits) >= minDigits:
        guaranteed_chars.extend(random.sample(digits, minDigits))
    if minSpecial > 0 and len(specialChars) >= minSpecial:
        guaranteed_chars.extend(random.sample(specialChars, minSpecial))

    # fill the rest of the password length (required text is inserted intact below)
    remaining_length = length - len(guaranteed_chars) - len(requiredText)
    if remaining_length < 0:
        return "error: length too short for requirements and required text"

    if remaining_length > 0:
        password_list.extend(random.choices(characters, k=remaining_length))
    
    password_list.extend(guaranteed_chars)
    
    # shuffle the final password list to ensure randomness
    random.shuffle(password_list)
    
    final_password = "".join(password_list)

    # insert the required text in one piece at a random position
    if requiredText:
        insert_at = random.randrange(len(final_password) + 1)
        final_password = final_password[:insert_at] + requiredText + final_password[insert_at:]

    # add dashes
    if useDashes and dashSpacing > 0:
        return '-'.join(final_password[i:i+dashSpacing] for i in range(0, len(final_password), dashSpacing))

    return final_password
