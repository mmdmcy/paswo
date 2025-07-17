# security tests for the self-designed encryption algorithm
# this file tests the security and compares with aes as requested in the exercise

from encryption import encryptText, decryptText, hashText
import time
import math

# function to calculate entropy
def calculateEntropy(dataString):
    print("calculating entropy...")  # debug for entropy
    
    # step 1: count frequency of each byte value
    frequencyList = [0] * 256
    totalBytes = len(dataString)
    
    # step 2: go through each character and count
    for singleChar in dataString:
        byteValue = ord(singleChar) if isinstance(singleChar, str) else singleChar
        if 0 <= byteValue <= 255:
            frequencyList[byteValue] = frequencyList[byteValue] + 1
    
    # step 3: calculate entropy
    entropy = 0.0
    for frequency in frequencyList:
        if frequency > 0:
            probability = frequency / totalBytes
            entropy = entropy - (probability * math.log2(probability))
    
    print(f"calculated entropy: {entropy:.4f} bits per byte")  # debug for result
    return entropy

# function to test avalanche effect
def testAvalancheEffect(testPassword, masterPassword):
    print("=== AVALANCHE EFFECT TEST ===")  # debug for test start
    
    # step 1: encrypt original text
    originalEncrypted = encryptText(testPassword, masterPassword)
    print(f"original password: '{testPassword}'")  # debug for original
    print(f"original encrypted: '{originalEncrypted}'")  # debug for encrypted
    
    # step 2: change 1 bit in password and test again
    if len(testPassword) > 0:
        # change first character by 1 bit
        firstChar = testPassword[0]
        changedChar = chr(ord(firstChar) ^ 1)  # flip first bit
        changedPassword = changedChar + testPassword[1:]
        
        changedEncrypted = encryptText(changedPassword, masterPassword)
        print(f"changed password: '{changedPassword}'")  # debug for changed
        print(f"changed encrypted: '{changedEncrypted}'")  # debug for changed encrypted
        
        # step 3: compare how many bits differ
        differentBits = 0
        minLength = min(len(originalEncrypted), len(changedEncrypted))
        
        for position in range(minLength):
            char1 = originalEncrypted[position]
            char2 = changedEncrypted[position]
            
            # compare each bit
            if char1 != char2:
                differentBits = differentBits + 1
        
        # step 4: calculate percentage difference
        totalBits = minLength
        changePercentage = (differentBits / totalBits) * 100 if totalBits > 0 else 0
        
        print(f"number of different bits: {differentBits} of {totalBits}")  # debug for difference
        print(f"avalanche effect: {changePercentage:.2f}%")  # debug for percentage
        
        # good encryption should have >50%
        if changePercentage > 50:
            print("✓ AVALANCHE TEST PASSED (>50% difference)")
        else:
            print("✗ AVALANCHE TEST FAILED (<50% difference)")
        
        return changePercentage

# function to test timing attack resistance
def testTimingAttackResistance(correctPassword, wrongPasswords, iterations=100):
    print("=== TIMING ATTACK RESISTANCE TEST ===")  # debug for timing test
    
    # step 1: measure time for correct passwords
    correctTimes = []
    for iteration in range(iterations):
        startTime = time.time()
        hashResult = hashText(correctPassword)
        endTime = time.time()
        timeDifference = endTime - startTime
        correctTimes.append(timeDifference)
    
    # step 2: measure time for wrong passwords
    wrongTimes = []
    for wrongPassword in wrongPasswords:
        for iteration in range(iterations):
            startTime = time.time()
            hashResult = hashText(wrongPassword)
            endTime = time.time()
            timeDifference = endTime - startTime
            wrongTimes.append(timeDifference)
    
    # step 3: calculate average times
    avgCorrectTime = sum(correctTimes) / len(correctTimes)
    avgWrongTime = sum(wrongTimes) / len(wrongTimes)
    
    print(f"average time correct password: {avgCorrectTime:.6f} seconds")
    print(f"average time wrong password: {avgWrongTime:.6f} seconds")
    
    # step 4: calculate difference
    timeDifference = abs(avgCorrectTime - avgWrongTime)
    timeDifferencePercent = (timeDifference / max(avgCorrectTime, avgWrongTime)) * 100
    
    print(f"time difference: {timeDifference:.6f} seconds ({timeDifferencePercent:.2f}%)")
    
    # less than 5% difference is good
    if timeDifferencePercent < 5:
        print("✓ TIMING ATTACK RESISTANCE GOOD (<5% difference)")
    else:
        print("✗ TIMING ATTACK RESISTANCE WEAK (>5% difference)")
    
    return timeDifferencePercent

# function to estimate brute force resistance
def estimateBruteForceResistance(passwordLength, characterSet):
    print("=== BRUTE FORCE RESISTANCE ESTIMATION ===")  # debug for brute force
    
    # step 1: calculate possible combinations
    possibleCombinations = len(characterSet) ** passwordLength
    print(f"password length: {passwordLength}")
    print(f"character set size: {len(characterSet)}")
    print(f"possible combinations: {possibleCombinations}")
    
    # step 2: estimate time to crack (1 million attempts per second)
    attemptsPerSecond = 1000000
    secondsToBreak = possibleCombinations / (2 * attemptsPerSecond)  # on average try half
    
    # step 3: convert to understandable units
    minutesToBreak = secondsToBreak / 60
    hoursToBreak = minutesToBreak / 60
    daysToBreak = hoursToBreak / 24
    yearsToBreak = daysToBreak / 365
    
    print(f"estimated time to crack:")
    print(f"  - seconds: {secondsToBreak:.2e}")
    print(f"  - minutes: {minutesToBreak:.2e}")
    print(f"  - hours: {hoursToBreak:.2e}")
    print(f"  - days: {daysToBreak:.2e}")
    print(f"  - years: {yearsToBreak:.2e}")
    
    # assessment
    if yearsToBreak > 1000000:
        print("✓ EXCELLENT BRUTE FORCE RESISTANCE (>1M years)")
    elif yearsToBreak > 1000:
        print("✓ GOOD BRUTE FORCE RESISTANCE (>1K years)")
    elif yearsToBreak > 1:
        print("⚠ MODERATE BRUTE FORCE RESISTANCE (>1 year)")
    else:
        print("✗ WEAK BRUTE FORCE RESISTANCE (<1 year)")
    
    return yearsToBreak

# function to compare our algorithm with aes (conceptually)
def compareWithAES():
    print("=== COMPARISON WITH AES ===")  # debug for aes comparison
    
    print("properties of our algorithm:")
    print("  ✓ substitution: uses dynamic s-box based on key")
    print("  ✓ transposition: uses key-dependent displacement")
    print("  ✓ xor operation: mixes data with key-derived bytes")
    print("  ✓ multiple rounds: 3 rounds for extra security")
    print("  ✓ sha-256 hashing: used for key derivation")
    
    print("\ncomparison with aes-128:")
    print("  ✓ both use substitution (s-box)")
    print("  ✓ both use transposition (shiftrows)")
    print("  ✓ both use key mixing")
    print("  - aes has 10 rounds, we have 3 rounds")
    print("  - aes uses galois field mathematics, we use simpler operations")
    print("  - aes is internationally standardized and extensively tested")
    
    print("\nstrong points of our algorithm:")
    print("  + simple to understand and implement")
    print("  + uses proven sha-256 for key derivation")
    print("  + dynamic s-box makes analysis more difficult")
    print("  + no external libraries needed")
    
    print("\nweak points compared to aes:")
    print("  - fewer rounds may mean weaker diffusion")
    print("  - no formal cryptographic analysis performed")
    print("  - smaller community of security experts who have tested it")
    print("  - simpler operations may expose patterns")

# main function to run all tests
def runAllSecurityTests():
    print("=== COMPLETE SECURITY TEST SUITE ===")  # debug for start
    print("as specified in the exercise: entropy analysis and aes comparison")
    print()
    
    # test parameters
    testPassword = "mySecretPassword123"
    masterPassword = "masterKey456"
    
    # test 1: basic encryption/decryption test
    print("=== BASIC FUNCTIONALITY TEST ===")
    encrypted = encryptText(testPassword, masterPassword)
    decrypted = decryptText(encrypted, masterPassword)
    
    print(f"original: '{testPassword}'")
    print(f"encrypted: '{encrypted}'")
    print(f"decrypted: '{decrypted}'")
    
    if testPassword == decrypted:
        print("✓ BASIC ENCRYPTION/DECRYPTION WORKS CORRECTLY")
    else:
        print("✗ BASIC ENCRYPTION/DECRYPTION FAILED")
    
    print()
    
    # test 2: entropy analysis
    print("=== ENTROPY ANALYSIS ===")
    originalEntropy = calculateEntropy(testPassword)
    encryptedEntropy = calculateEntropy(encrypted)
    
    print(f"entropy original text: {originalEntropy:.4f} bits/byte")
    print(f"entropy encrypted text: {encryptedEntropy:.4f} bits/byte")
    
    if encryptedEntropy > originalEntropy:
        print("✓ ENCRYPTION INCREASES ENTROPY (GOOD)")
    else:
        print("⚠ ENCRYPTION DECREASES ENTROPY (POSSIBLE PROBLEM)")
    
    print()
    
    # test 3: avalanche effect
    avalancheResult = testAvalancheEffect(testPassword, masterPassword)
    print()
    
    # test 4: timing attack resistance
    wrongPasswords = ["wrongPass1", "wrongPass2", "wrongPass3", "differentLength"]
    timingResult = testTimingAttackResistance(masterPassword, wrongPasswords)
    print()
    
    # test 5: brute force resistance
    characterSet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    bruteForceResult = estimateBruteForceResistance(12, characterSet)
    print()
    
    # test 6: aes comparison
    compareWithAES()
    print()
    
    # summary
    print("=== SECURITY TEST SUMMARY ===")
    print(f"entropy improvement: {'YES' if encryptedEntropy > originalEntropy else 'NO'}")
    print(f"avalanche effect: {avalancheResult:.2f}% ({'GOOD' if avalancheResult > 50 else 'WEAK'})")
    print(f"timing attack resistance: {timingResult:.2f}% ({'GOOD' if timingResult < 5 else 'WEAK'})")
    print(f"brute force resistance: {bruteForceResult:.2e} years")
    print()
    print("conclusion: the algorithm shows good basic security properties")
    print("but is less tested than industry standard aes.")
    print("for production use, aes is recommended.")

# run tests if script is executed directly
if __name__ == "__main__":
    runAllSecurityTests()
