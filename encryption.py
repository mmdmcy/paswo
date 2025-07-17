# function to hash text with sha-256 algorithm
def hashText(inputText):
    # step 1: create the sha-256 constants (these are fixed numbers)
    sha256Constants = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    
    # step 2: create the initial hash values (these are also fixed numbers)
    hashValues = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    
    # step 3: convert text to bytes
    messageBytes = []
    for singleCharacter in inputText:
        byteValue = ord(singleCharacter)
        messageBytes.append(byteValue)
    
    # step 4: remember how many bits we had
    originalLengthBits = len(messageBytes) * 8
    
    # step 5: add a special byte (this is required for sha-256)
    messageBytes.append(0x80)
    
    # step 6: add zeros until we have the right length
    while (len(messageBytes) % 64) != 56:
        messageBytes.append(0x00)
    
    # step 7: add the original length to the end
    for byteIndex in range(8):
        shiftValue = 8 * (7 - byteIndex)
        byteValue = (originalLengthBits >> shiftValue) & 0xff
        messageBytes.append(byteValue)
    
    # step 8: process the bytes in chunks of 64
    for chunkStart in range(0, len(messageBytes), 64):
        # step 8a: create 16 words of 4 bytes each
        messageWords = []
        for wordIndex in range(16):
            wordValue = 0
            for byteIndex in range(4):
                bytePosition = chunkStart + wordIndex * 4 + byteIndex
                wordValue = wordValue * 256
                wordValue = wordValue + messageBytes[bytePosition]
            messageWords.append(wordValue)
        
        # step 8b: create 48 additional words (total 64)
        for wordIndex in range(16, 64):
            word15Back = messageWords[wordIndex - 15]
            word2Back = messageWords[wordIndex - 2]
            
            # do some calculations (this is sha-256 algorithm)
            s0Part1 = (word15Back >> 7) | (word15Back << 25)
            s0Part2 = (word15Back >> 18) | (word15Back << 14)
            s0Part3 = word15Back >> 3
            s0Value = s0Part1 ^ s0Part2 ^ s0Part3
            
            s1Part1 = (word2Back >> 17) | (word2Back << 15)
            s1Part2 = (word2Back >> 19) | (word2Back << 13)
            s1Part3 = word2Back >> 10
            s1Value = s1Part1 ^ s1Part2 ^ s1Part3
            
            newWord = messageWords[wordIndex - 16] + s0Value + messageWords[wordIndex - 7] + s1Value
            newWord = newWord & 0xffffffff
            messageWords.append(newWord)
        
        # step 8c: get the current hash values
        aValue = hashValues[0]
        bValue = hashValues[1]
        cValue = hashValues[2]
        dValue = hashValues[3]
        eValue = hashValues[4]
        fValue = hashValues[5]
        gValue = hashValues[6]
        hValue = hashValues[7]
        
        # step 8d: do 64 rounds of calculations
        for roundIndex in range(64):
            # calculate s1 value
            s1Part1 = (eValue >> 6) | (eValue << 26)
            s1Part2 = (eValue >> 11) | (eValue << 21)
            s1Part3 = (eValue >> 25) | (eValue << 7)
            s1Final = s1Part1 ^ s1Part2 ^ s1Part3
            
            # calculate ch value
            chValue = (eValue & fValue) ^ (~eValue & gValue)
            
            # calculate temp1
            temp1 = hValue + s1Final + chValue + sha256Constants[roundIndex] + messageWords[roundIndex]
            temp1 = temp1 & 0xffffffff
            
            # calculate s0 value
            s0Part1 = (aValue >> 2) | (aValue << 30)
            s0Part2 = (aValue >> 13) | (aValue << 19)
            s0Part3 = (aValue >> 22) | (aValue << 10)
            s0Final = s0Part1 ^ s0Part2 ^ s0Part3
            
            # calculate maj value
            majValue = (aValue & bValue) ^ (aValue & cValue) ^ (bValue & cValue)
            
            # calculate temp2
            temp2 = s0Final + majValue
            temp2 = temp2 & 0xffffffff
            
            # shift all values through
            hValue = gValue
            gValue = fValue
            fValue = eValue
            eValue = (dValue + temp1) & 0xffffffff
            dValue = cValue
            cValue = bValue
            bValue = aValue
            aValue = (temp1 + temp2) & 0xffffffff
        
        # step 8e: add the calculated values to the hash
        hashValues[0] = (hashValues[0] + aValue) & 0xffffffff
        hashValues[1] = (hashValues[1] + bValue) & 0xffffffff
        hashValues[2] = (hashValues[2] + cValue) & 0xffffffff
        hashValues[3] = (hashValues[3] + dValue) & 0xffffffff
        hashValues[4] = (hashValues[4] + eValue) & 0xffffffff
        hashValues[5] = (hashValues[5] + fValue) & 0xffffffff
        hashValues[6] = (hashValues[6] + gValue) & 0xffffffff
        hashValues[7] = (hashValues[7] + hValue) & 0xffffffff
    
    # step 9: convert the hash to text
    finalHashText = ''
    for singleHashValue in hashValues:
        # convert number to hex
        hexText = hex(singleHashValue)[2:]
        # make sure it's 8 characters long
        while len(hexText) < 8:
            hexText = '0' + hexText
        finalHashText = finalHashText + hexText
    
    return finalHashText

# function to create substitution table
def createSubstitutionTable(keyValue):
    # step 1: create a list with numbers from 0 to 255
    substitutionTable = []
    for numberValue in range(256):
        substitutionTable.append(numberValue)
    
    # step 2: hash the key
    keyHashText = hashText(keyValue)
    
    # step 3: convert the hash to a large number
    keyNumber = int(keyHashText, 16)
    
    # step 4: mix the table first time
    for indexValue in range(256):
        swapPosition = (indexValue + keyNumber) % 256
        # swap the values
        tempValue = substitutionTable[indexValue]
        substitutionTable[indexValue] = substitutionTable[swapPosition]
        substitutionTable[swapPosition] = tempValue
    
    # step 5: mix the table second time for extra security
    for indexValue in range(256):
        mixNumber = (substitutionTable[indexValue] + keyNumber + indexValue) % 256
        swapPosition = mixNumber % 256
        # swap the values
        tempValue = substitutionTable[indexValue]
        substitutionTable[indexValue] = substitutionTable[swapPosition]
        substitutionTable[swapPosition] = tempValue
    
    return substitutionTable

# function to do transposition
def transposeTextValues(inputTextValues, keyValue):
    # step 1: hash the key
    keyHashText = hashText(keyValue)
    
    # step 2: calculate how long the text is
    textLength = len(inputTextValues)
    
    # step 3: create a new empty list
    resultValues = []
    for indexValue in range(textLength):
        resultValues.append(0)
    
    # step 4: calculate how much we need to shift
    keyNumber = int(keyHashText, 16) % textLength
    if keyNumber == 0:
        keyNumber = 1
    
    # step 5: move each element to new position
    for indexValue in range(textLength):
        oldPosition = indexValue
        newPosition = (indexValue + keyNumber) % textLength
        resultValues[newPosition] = inputTextValues[oldPosition]
    
    return resultValues

# function to do inverse transposition
def inverseTransposeTextValues(inputTextValues, keyValue):
    # step 1: hash the key
    keyHashText = hashText(keyValue)
    
    # step 2: calculate how long the text is
    textLength = len(inputTextValues)
    
    # step 3: create a new empty list
    resultValues = []
    for indexValue in range(textLength):
        resultValues.append(0)
    
    # step 4: calculate how much we need to shift back
    keyNumber = int(keyHashText, 16) % textLength
    if keyNumber == 0:
        keyNumber = 1
    
    # step 5: move each element back to old position
    for indexValue in range(textLength):
        currentPosition = indexValue
        oldPosition = (indexValue - keyNumber) % textLength
        resultValues[oldPosition] = inputTextValues[currentPosition]
    
    return resultValues

# function to create key for xor
def createXorKeyValues(masterPasswordValue, lengthValue):
    # step 1: hash the password
    keyHashText = hashText(masterPasswordValue)
    
    # step 2: create empty list for the key
    xorKeyValues = []
    
    # step 3: start at the beginning of the hash
    hashPosition = 0
    
    # step 4: create enough key bytes
    for indexValue in range(lengthValue):
        # step 4a: check if we're at the end of the hash
        if hashPosition >= len(keyHashText):
            hashPosition = 0  # start over
        
        # step 4b: take two characters from the hash
        hexChar1 = keyHashText[hashPosition]
        hashPosition = hashPosition + 1
        
        if hashPosition >= len(keyHashText):
            hexChar2 = '0'
        else:
            hexChar2 = keyHashText[hashPosition]
            hashPosition = hashPosition + 1
        
        # step 4c: convert the two hex characters to a number
        hexPair = hexChar1 + hexChar2
        keyByte = int(hexPair, 16)
        
        # step 4d: add to the key list
        xorKeyValues.append(keyByte)
    
    return xorKeyValues

# function to convert binary data to safe text
def encodeBinaryToText(binaryValuesList):
    # step 1: start with empty text
    encodedText = ''
    
    # step 2: go through each number in the list
    for singleByte in binaryValuesList:
        # step 3: make sure the number is between 0 and 255
        safeByte = singleByte % 256
        
        # step 4: convert the number to hex
        hexText = hex(safeByte)[2:]  # [2:] removes the '0x'
        
        # step 5: make sure it always has 2 characters
        if len(hexText) == 1:
            hexText = '0' + hexText
        
        # step 6: add to the text
        encodedText = encodedText + hexText
    
    return encodedText

# function to convert safe text back to binary data
def decodeTextToBinary(encodedText):
    # step 1: create empty list for numbers
    binaryValuesList = []
    
    # step 2: go through the text in steps of 2
    for position in range(0, len(encodedText), 2):
        # step 3: take 2 characters
        hexChar1 = encodedText[position]
        
        if position + 1 < len(encodedText):
            hexChar2 = encodedText[position + 1]
        else:
            hexChar2 = '0'  # if there's only 1 character left
        
        # step 4: convert the 2 hex characters to number
        hexPair = hexChar1 + hexChar2
        byteValue = int(hexPair, 16)
        
        # step 5: add to the list
        binaryValuesList.append(byteValue)
    
    return binaryValuesList
# function to encrypt text
def encryptText(inputText, masterPasswordValue):
    # step 1: create substitution table
    substitutionTable = createSubstitutionTable(masterPasswordValue)
    
    # step 2: convert text to ascii numbers
    asciiNumbers = []
    for singleCharacter in inputText:
        asciiValue = ord(singleCharacter)
        asciiNumbers.append(asciiValue)
    
    # step 3: do three rounds of encryption (like aes does)
    currentNumbers = asciiNumbers
    
    for roundNumber in range(3):
        print(f"encryption round {roundNumber + 1}")  # debug for round
        
        # step 3a: substitution (replace each number)
        substitutedNumbers = []
        for singleNumber in currentNumbers:
            tablePosition = singleNumber % 256
            newNumber = substitutionTable[tablePosition]
            substitutedNumbers.append(newNumber)
        
        # step 3b: transposition (move numbers)
        transposedNumbers = transposeTextValues(substitutedNumbers, masterPasswordValue)
        
        # step 3c: xor with key (mix with password)
        xorKey = createXorKeyValues(masterPasswordValue, len(transposedNumbers))
        xorNumbers = []
        for position in range(len(transposedNumbers)):
            xorResult = transposedNumbers[position] ^ xorKey[position]
            xorNumbers.append(xorResult)
        
        # step 3d: ready for next round
        currentNumbers = xorNumbers
    
    # step 4: convert to safe text for storage
    safeText = encodeBinaryToText(currentNumbers)
    return safeText

# function to decrypt text
def decryptText(encryptedText, masterPasswordValue):
    # step 1: create substitution table
    substitutionTable = createSubstitutionTable(masterPasswordValue)
    
    # step 2: create inverse substitution table
    inverseTable = []
    for position in range(256):
        inverseTable.append(0)
    
    for position in range(256):
        originalValue = position
        newValue = substitutionTable[position]
        inverseTable[newValue] = originalValue
    
    # step 3: convert safe text back to numbers
    encryptedNumbers = decodeTextToBinary(encryptedText)
    
    # step 4: do three rounds back (reverse order)
    currentNumbers = encryptedNumbers
    
    for roundNumber in range(3):
        print(f"decryption round {roundNumber + 1}")  # debug for round
        
        # step 4a: xor back (undo mix with password)
        xorKey = createXorKeyValues(masterPasswordValue, len(currentNumbers))
        xorNumbers = []
        for position in range(len(currentNumbers)):
            xorResult = currentNumbers[position] ^ xorKey[position]
            xorNumbers.append(xorResult)
        
        # step 4b: inverse transposition (move numbers back)
        transposedNumbers = inverseTransposeTextValues(xorNumbers, masterPasswordValue)
        
        # step 4c: inverse substitution (numbers back)
        substitutedNumbers = []
        for singleNumber in transposedNumbers:
            tablePosition = singleNumber % 256
            originalNumber = inverseTable[tablePosition]
            substitutedNumbers.append(originalNumber)
        
        # step 4d: ready for next round
        currentNumbers = substitutedNumbers
    
    # step 5: convert numbers back to text
    finalText = ''
    for singleNumber in currentNumbers:
        character = chr(singleNumber)
        finalText = finalText + character
    
    return finalText