from encryption import encryptText, decryptText

# function to save passwords in json format as specified
def savePasswordsToFile(passwordsDictionary, masterPasswordValue):
    print("saving passwords to passwords.json...")  # debug for saving
    
    # step 1: start with opening json file
    jsonText = ""
    jsonText = jsonText + "{\n"
    
    # step 2: loop through all passwords one by one
    numberOfPasswords = len(passwordsDictionary)
    currentPasswordNumber = 0
    
    for siteValue in passwordsDictionary:
        # step 3: get the password data for this site
        passwordData = passwordsDictionary[siteValue]
        
        # step 4: handle both old format (string) and new format (dict)
        if isinstance(passwordData, dict):
            # new format with username, email, password
            passwordDataJson = {
                'username': passwordData.get('username', ''),
                'email': passwordData.get('email', ''),
                'password': passwordData.get('password', '')
            }
            # convert to string for encryption
            passwordValueToEncrypt = str(passwordDataJson)
        else:
            # old format - just the password string
            passwordValueToEncrypt = passwordData
        
        # step 5: encrypt the password data
        encryptedPasswordValue = encryptText(passwordValueToEncrypt, masterPasswordValue)
        
        # step 6: make the site name safe for json
        safeSiteName = ""
        for characterValue in siteValue:
            if characterValue == '"':
                safeSiteName = safeSiteName + '\\"'
            else:
                safeSiteName = safeSiteName + characterValue
        
        # step 7: add the line to json text
        jsonText = jsonText + '  "'
        jsonText = jsonText + safeSiteName
        jsonText = jsonText + '": "'
        jsonText = jsonText + encryptedPasswordValue
        jsonText = jsonText + '"'
        
        # step 8: add comma if it's not the last password
        currentPasswordNumber = currentPasswordNumber + 1
        if currentPasswordNumber < numberOfPasswords:
            jsonText = jsonText + ","
        
        # step 9: go to next line
        jsonText = jsonText + "\n"
    
    # step 10: close the json file
    jsonText = jsonText + "}"
    
    # step 11: write everything to file
    fileHandle = open('passwords.json', 'w')
    fileHandle.write(jsonText)
    fileHandle.close()
    print("passwords saved to passwords.json")  # debug for location

# function to load passwords from json format
def loadPasswordsFromFile(masterPasswordValue):
    print("loading passwords from passwords.json...")  # debug for loading
    # step 1: create empty dictionary for passwords
    passwordsDictionary = {}
    
    # step 2: try to open file
    try:
        fileHandle = open('passwords.json', 'r')
    except FileNotFoundError:
        print("passwords.json not found - starting with empty password list")  # debug for new file
        return passwordsDictionary
    
    try:
        jsonContent = fileHandle.read()
        fileHandle.close()
        print("file read")  # debug for reading
        
        # step 3: clean the json string
        cleanContent = jsonContent.strip()
        
        # step 4: remove { and }
        if cleanContent.startswith('{'):
            cleanContent = cleanContent[1:]
        if cleanContent.endswith('}'):
            cleanContent = cleanContent[:-1]
        
        # step 5: check if there is content
        if cleanContent.strip() == "":
            print("empty file found")  # debug for empty
            return passwordsDictionary
        
        # step 6: split entries on commas
        allEntries = cleanContent.split(',')
        
        # step 7: go through each entry
        for singleEntry in allEntries:
            # step 7a: clean entry
            cleanEntry = singleEntry.strip()
            
            # step 7b: check if there is a colon in it
            if ':' not in cleanEntry:
                continue  # skip if no colon
            
            # step 7c: find all quotation marks
            firstQuote = cleanEntry.find('"')
            secondQuote = cleanEntry.find('"', firstQuote + 1)
            thirdQuote = cleanEntry.find('"', secondQuote + 1)
            fourthQuote = cleanEntry.find('"', thirdQuote + 1)
            
            # step 7d: check if all quotes are found
            if firstQuote == -1:
                continue  # skip if quotes are missing
            if secondQuote == -1:
                continue  # skip if quotes are missing
            if thirdQuote == -1:
                continue  # skip if quotes are missing
            if fourthQuote == -1:
                continue  # skip if quotes are missing
            
            # step 7e: extract site name
            siteValue = cleanEntry[firstQuote + 1:secondQuote]
            
            # step 7f: extract encrypted password
            encryptedPasswordValue = cleanEntry[thirdQuote + 1:fourthQuote]
            
            # step 7g: undo quotes in site name
            siteValue = siteValue.replace('\\"', '"')
            
            try:
                # step 7h: decrypt the password
                decryptedValue = decryptText(encryptedPasswordValue, masterPasswordValue)
                
                # step 7i: try to parse as new format (dict), fallback to old format (string)
                if decryptedValue.startswith("{'") or decryptedValue.startswith('{"'):
                    # convert string back to dictionary
                    passwordData = eval(decryptedValue)
                    if isinstance(passwordData, dict) and 'password' in passwordData:
                        # new format - store as dictionary
                        passwordsDictionary[siteValue] = passwordData
                    else:
                        # old format - store as string
                        passwordsDictionary[siteValue] = decryptedValue
                else:
                    # old format - store as string
                    passwordsDictionary[siteValue] = decryptedValue
                
                print(f"password loaded for: {siteValue}")  # debug for entry
            except Exception as e:
                print(f"Error decrypting password for {siteValue}: {str(e)}")
                continue
    
    except Exception as e:
        print(f"Error loading passwords: {str(e)}")  # debug for error
        raise  # Re-raise the exception to be handled by the caller
    
    # step 8: return the dictionary
    return passwordsDictionary