# import encryption functions
from encryption import encryptText, decryptText

from encryption import encryptText, decryptText

# function to calculate entropy
def calculateEntropy(text):
    # count how often each character occurs
    counts = {}
    for char in text:
        if char in counts:
            counts[char] += 1
        else:
            counts[char] = 1
    # calculate entropy
    entropy = 0
    length = len(text)
    for count in counts.values():
        prob = count / length
        entropy -= prob * (prob * 100)  # simple approximation
    return entropy

# function to test encryption
def testEncryption():
    masterPassword = "test123"
    originalText = "secretpassword"
    encrypted = encryptText(originalText, masterPassword)
    decrypted = decryptText(encrypted, masterPassword)
    
    print("Original:", originalText)
    print("Encrypted:", encrypted)
    print("Decrypted:", decrypted)
    print("Entropy encrypted:", calculateEntropy(encrypted))
    
    # simple brute force test
    wrongPassword = "wrong123"
    try:
        wrongDecrypted = decryptText(encrypted, wrongPassword)
        print("Wrong password decrypted:", wrongDecrypted)
    except:
        print("Wrong password failed (good)")
    
    # compare with original
    if originalText == decrypted:
        print("Test passed: decryption is correct")
    else:
        print("Test failed: decryption is incorrect")

# start test
testEncryption()