# test file for visual password strength indicator

# create simple test function
def testPasswordStrengthIndicator():
    print("=== TEST PASSWORD STRENGTH INDICATOR ===")
    
    # test different passwords
    testPasswords = [
        "",  # empty
        "abc",  # weak - short, only letters
        "password",  # weak - no numbers/special chars
        "Password1",  # moderate - uppercase and numbers
        "Password123",  # moderate - somewhat longer
        "Password123!",  # strong - has everything
        "MySecurePassword123!@#",  # very strong - long and complex
    ]
    
    # define strength check function
    def checkPasswordStrength(passwordString):
        if len(passwordString) == 0:
            return 0, "no password", "gray"
        
        strengthScore = 0
        hasLowerCase = False
        hasUpperCase = False
        hasDigits = False
        hasSpecialChars = False
        
        for character in passwordString:
            if character.islower():
                hasLowerCase = True
            elif character.isupper():
                hasUpperCase = True
            elif character.isdigit():
                hasDigits = True
            elif character in "!@#$%^&*()_+-=[]{}|;':\",./<>?":
                hasSpecialChars = True
        
        if len(passwordString) >= 8:
            strengthScore += 2
        if len(passwordString) >= 12:
            strengthScore += 1
        if hasLowerCase:
            strengthScore += 1
        if hasUpperCase:
            strengthScore += 1
        if hasDigits:
            strengthScore += 1
        if hasSpecialChars:
            strengthScore += 2
        
        if strengthScore >= 7:
            strengthText = "very strong"
            strengthColor = "green"
        elif strengthScore >= 5:
            strengthText = "strong"
            strengthColor = "orange"
        elif strengthScore >= 3:
            strengthText = "moderate"
            strengthColor = "yellow"
        else:
            strengthText = "weak"
            strengthColor = "red"
        
        return strengthScore, strengthText, strengthColor
    
    # test each password
    for testPassword in testPasswords:
        print(f"\nTesting password: '{testPassword}'")
        
        score, text, color = checkPasswordStrength(testPassword)
        print(f"  Score: {score}")
        print(f"  Strength: {text}")
        print(f"  Color: {color}")
        
        # check criteria
        hasLower = any(c.islower() for c in testPassword)
        hasUpper = any(c.isupper() for c in testPassword)
        hasDigit = any(c.isdigit() for c in testPassword)
        hasSpecial = any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in testPassword)
        
        print(f"  Length: {len(testPassword)}")
        print(f"  Lowercase: {hasLower}")
        print(f"  Uppercase: {hasUpper}")
        print(f"  Numbers: {hasDigit}")
        print(f"  Special chars: {hasSpecial}")
    
    print("\n=== TEST COMPLETED ===")

# run test
testPasswordStrengthIndicator()
