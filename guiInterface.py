from tkinter import Tk, Frame, Label, Entry, Button, Checkbutton, IntVar, END, Listbox, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH, messagebox
from encryption import hashText
from fileHandler import savePasswordsToFile, loadPasswordsFromFile
from passwordGenerator import generatePasswordString

# function to check if file exists
def checkIfFileExists(fileNameString):
    print(f"checking if file exists: {fileNameString}")  # debug for file
    try:
        fileHandle = open(fileNameString, 'r')
        fileHandle.close()
        return True
    except:
        return False

# function to check if master password is actually set
def checkIfMasterPasswordIsSet():
    print("checking if master password is actually set...")  # debug
    try:
        # step 1: check if file exists
        if not checkIfFileExists('master_password.json'):
            print("master_password.json does not exist")  # debug
            return False
        
        # step 2: load the master password
        hashedPassword = loadMasterPasswordFromFile()
        
        # step 3: check if there is a valid hash
        if hashedPassword is None or hashedPassword == "":
            print("no valid hash found in master_password.json")  # debug
            return False
        
        print(f"valid hash found: {hashedPassword[:10]}...")  # debug (show only first 10 characters)
        return True
    except:
        print("error checking master password status")  # debug
        return False

# function to save master password in json format
def saveMasterPasswordToFile(masterPasswordString):
    print("hashing and saving master password to json...")  # debug for saving
    # step 1: hash the master password
    hashedPasswordString = hashText(masterPasswordString)
    
    # step 2: create json string manually
    jsonString = "{\n"
    jsonString = jsonString + '  "master_password_hash": "'
    jsonString = jsonString + hashedPasswordString
    jsonString = jsonString + '"\n'
    jsonString = jsonString + "}"
    
    # step 3: write to file
    fileHandle = open('master_password.json', 'w')
    fileHandle.write(jsonString)
    fileHandle.close()
    print("master password saved to master_password.json")  # debug for location

# function to load master password from json format
def loadMasterPasswordFromFile():
    print("loading master password from json...")  # debug for loading
    try:
        # step 1: check if json file exists
        if not checkIfFileExists('master_password.json'):
            return None
        
        # step 2: read the file
        fileHandle = open('master_password.json', 'r')
        jsonContent = fileHandle.read()
        fileHandle.close()
        
        # step 3: parse json manually
        cleanContent = jsonContent.strip()
        
        # step 4: remove { and }
        if cleanContent.startswith('{'):
            cleanContent = cleanContent[1:]
        if cleanContent.endswith('}'):
            cleanContent = cleanContent[:-1]
        
        # step 5: find the hash value
        if '"master_password_hash":' in cleanContent:
            # find first and second quote after the colon
            colonPosition = cleanContent.find(':')
            firstQuote = cleanContent.find('"', colonPosition)
            secondQuote = cleanContent.find('"', firstQuote + 1)
            
            if firstQuote != -1 and secondQuote != -1:
                hashedPassword = cleanContent[firstQuote + 1:secondQuote]
                return hashedPassword
        
        return None
    except:
        return None

# function to wipe all data and start over
def wipeMasterPasswordAndRestart():
    print("wiping all password data...")  # debug for wiping
    
    # step 1: create empty json for master password
    emptyMasterJson = "{\n"
    emptyMasterJson = emptyMasterJson + '  "master_password_hash": ""\n'
    emptyMasterJson = emptyMasterJson + "}"
    
    # step 2: write empty master password file
    try:
        fileHandle = open('master_password.json', 'w')
        fileHandle.write(emptyMasterJson)
        fileHandle.close()
        print("master_password.json wiped")
    except:
        print("error wiping master_password.json")
    
    # step 3: create empty json for passwords
    emptyPasswordsJson = "{}"
    
    # step 4: write empty passwords file
    try:
        fileHandle = open('passwords.json', 'w')
        fileHandle.write(emptyPasswordsJson)
        fileHandle.close()
        print("passwords.json wiped")
    except:
        print("error wiping passwords.json")
    
    return True

# function to start gui
def startGuiApplication():
    print("starting gui...")  # debug to check if function begins
    print("creating tkinter window...")  # debug for window creation
    # create window
    mainWindow = Tk()
    print("setting window title...")  # debug after window creation
    mainWindow.title("Password Manager")
    mainWindow.geometry("1200x800")  # Reasonable size that fits most screens
    mainWindow.minsize(1000, 700)  # Set minimum window size
    
    # variables
    print("initializing variables...")  # debug for variables
    masterPasswordString = ''
    passwordsDictionary = {}
    # special character variables
    exclamationVariable = IntVar(value=1)  # default on
    dollarVariable = IntVar(value=1)  # default on
    hashVariable = IntVar(value=1)  # default on
    questionVariable = IntVar(value=1)  # default on
    atVariable = IntVar(value=1)  # default on
    ampersandVariable = IntVar(value=1)  # default on
    asteriskVariable = IntVar(value=1)  # default on
    caretVariable = IntVar(value=1)  # default on (^)
    euroVariable = IntVar(value=1)  # default on (€)
    percentVariable = IntVar(value=1)  # default on (%)
    plusVariable = IntVar(value=1)  # default on (+)
    upperCaseVariable = IntVar(value=1)  # default on    
    # frame for new master password
    createPasswordFrame = Frame(mainWindow)
    createLabel = Label(createPasswordFrame, text="Create new master password:")
    createEntry = Entry(createPasswordFrame, show="*")
    confirmLabel = Label(createPasswordFrame, text="Confirm master password:")
    confirmEntry = Entry(createPasswordFrame, show="*")
    
      # frame for login
    print("creating login frame...")  # debug for login frame
    loginFrame = Frame(mainWindow)
    loginLabel = Label(loginFrame, text="Master password:")
    loginEntry = Entry(loginFrame, show="*")
    
    # frame for passwords
    print("creating main frame...")  # debug for main frame
    mainFrame = Frame(mainWindow)    
    # left frame for password generation
    leftFrame = Frame(mainFrame)
    leftFrame.config(width=500)  # Compact width
    
    # website info frame
    websiteInfoFrame = Frame(leftFrame)
    websiteInfoFrame.config(relief="solid", bd=1, padx=10, pady=10)
    Label(websiteInfoFrame, text="Website Information", font=("Arial", 12, "bold")).pack(pady=(0, 5))
    
    siteLabel = Label(websiteInfoFrame, text="Website name:", font=("Arial", 10, "bold"))
    siteEntry = Entry(websiteInfoFrame, width=30, font=("Arial", 10))
    
    usernameLabel = Label(websiteInfoFrame, text="Username:", font=("Arial", 10, "bold"))
    usernameEntry = Entry(websiteInfoFrame, width=30, font=("Arial", 10))
    
    emailLabel = Label(websiteInfoFrame, text="Email address:", font=("Arial", 10, "bold"))
    emailEntry = Entry(websiteInfoFrame, width=30, font=("Arial", 10))
    
    # password info frame
    passwordInfoFrame = Frame(leftFrame)
    passwordInfoFrame.config(relief="solid", bd=1, padx=10, pady=10)
    Label(passwordInfoFrame, text="Generated Password", font=("Arial", 12, "bold")).pack(pady=(0, 5))
    
    passwordLabel = Label(passwordInfoFrame, text="Password:", font=("Arial", 10, "bold"))
    passwordEntry = Entry(passwordInfoFrame, width=30, font=("Arial", 10))
    strengthLabel = Label(passwordInfoFrame, text="Strength: no password", fg="gray", font=("Arial", 9))
    
    # special characters frame - COMPACT DESIGN
    specialFrame = Frame(leftFrame)
    specialFrame.config(relief="solid", bd=1, padx=10, pady=10)
    Label(specialFrame, text="Password Options", font=("Arial", 12, "bold")).pack(pady=(0, 5))
    
    # Special characters in compact grid
    specialCharsFrame = Frame(specialFrame)
    Label(specialCharsFrame, text="Special chars:", font=("Arial", 10, "bold")).pack(anchor="w")
    
    # Row 1 of special characters
    specialRow1 = Frame(specialCharsFrame)
    exclamationCheck = Checkbutton(specialRow1, text="!", variable=exclamationVariable, font=("Arial", 9))
    dollarCheck = Checkbutton(specialRow1, text="$", variable=dollarVariable, font=("Arial", 9))
    hashCheck = Checkbutton(specialRow1, text="#", variable=hashVariable, font=("Arial", 9))
    questionCheck = Checkbutton(specialRow1, text="?", variable=questionVariable, font=("Arial", 9))
    atCheck = Checkbutton(specialRow1, text="@", variable=atVariable, font=("Arial", 9))
    
    # Row 2 of special characters
    specialRow2 = Frame(specialCharsFrame)
    ampersandCheck = Checkbutton(specialRow2, text="&", variable=ampersandVariable, font=("Arial", 9))
    asteriskCheck = Checkbutton(specialRow2, text="*", variable=asteriskVariable, font=("Arial", 9))
    caretCheck = Checkbutton(specialRow2, text="^", variable=caretVariable, font=("Arial", 9))
    euroCheck = Checkbutton(specialRow2, text="€", variable=euroVariable, font=("Arial", 9))
    percentCheck = Checkbutton(specialRow2, text="%", variable=percentVariable, font=("Arial", 9))
    plusCheck = Checkbutton(specialRow2, text="+", variable=plusVariable, font=("Arial", 9))
    
    # Other options in compact layout
    otherOptionsFrame = Frame(specialFrame)
    upperCaseCheck = Checkbutton(otherOptionsFrame, text="Uppercase", variable=upperCaseVariable, font=("Arial", 10))
    
    lengthFrame = Frame(otherOptionsFrame)
    lengthLabel = Label(lengthFrame, text="Length:", font=("Arial", 10))
    lengthEntry = Entry(lengthFrame, width=5, font=("Arial", 10))
    lengthEntry.insert(0, "12")
    
    # Required text - COMPACT and VISIBLE
    requiredFrame = Frame(otherOptionsFrame)
    requiredTextLabel = Label(requiredFrame, text="Required text:", font=("Arial", 10))
    requiredTextEntry = Entry(requiredFrame, width=20, font=("Arial", 10), bg="lightyellow")
    
    # action buttons frame - COMPACT
    buttonActionsFrame = Frame(leftFrame)
    buttonActionsFrame.config(relief="solid", bd=1, padx=10, pady=10)
    generateButton = Button(buttonActionsFrame, text="Generate Password", font=("Arial", 11, "bold"), bg="lightblue", width=15)
    addButton = Button(buttonActionsFrame, text="Add to List", font=("Arial", 11, "bold"), bg="lightgreen", width=15)
    
    # right frame for password list
    rightFrame = Frame(mainFrame)
    listLabel = Label(rightFrame, text="Saved Passwords:", font=("Arial", 12, "bold"))
    
    # listbox with scrollbar
    listFrame = Frame(rightFrame)
    scrollbar = Scrollbar(listFrame, orient=VERTICAL)
    passwordListbox = Listbox(listFrame, yscrollcommand=scrollbar.set, height=25, width=60, font=("Arial", 9))
    scrollbar.config(command=passwordListbox.yview)
    
    # buttons for password management
    buttonFrame = Frame(rightFrame)
    editButton = Button(buttonFrame, text="Edit", font=("Arial", 10, "bold"), bg="orange", width=8)
    deleteButton = Button(buttonFrame, text="Delete", font=("Arial", 10, "bold"), bg="lightcoral", width=8)
    refreshButton = Button(buttonFrame, text="Refresh", font=("Arial", 10, "bold"), bg="lightgray", width=8)
      # function to create new master password
    def createNewMasterPassword():
        nonlocal masterPasswordString, passwordsDictionary
        print("=== CREATING NEW MASTER PASSWORD ===")  # debug for start
        
        # step 1: get passwords
        password1 = createEntry.get()
        password2 = confirmEntry.get()
        print(f"first password: '{password1}'")  # debug for first password
        print(f"second password: '{password2}'")  # debug for second password
        print(f"length first password: {len(password1)} characters")  # debug for length
        print(f"length second password: {len(password2)} characters")  # debug for length
        
        # step 2: check if both passwords are filled
        if not password1:
            print("ERROR: first password is empty!")  # debug for empty
            createLabel.config(text="Password cannot be empty:")
            return
        
        if not password2:
            print("ERROR: second password is empty!")  # debug for empty
            createLabel.config(text="Confirmation cannot be empty:")
            return
        
        # step 3: check if passwords match
        if password1 == password2:
            print("✓ PASSWORDS MATCH!")  # debug for match
            print("new master password will be saved...")  # debug for saving
            
            # step 4: hash the password and show details
            print(f"password '{password1}' will be hashed with sha-256...")  # debug for hashing
            hashedPassword = hashText(password1)
            print(f"hash of new master password: {hashedPassword}")  # debug for hash
            print(f"hash length: {len(hashedPassword)} characters")  # debug for hash length
            
            masterPasswordString = password1
            saveMasterPasswordToFile(masterPasswordString)
            print("master password successfully saved to master_password.json")  # debug for success
            createPasswordFrame.pack_forget()
            mainFrame.pack(pady=20)
            updatePasswords()
            print("=== MASTER PASSWORD CREATED ===")  # debug for end
        else:
            print("✗ PASSWORDS DO NOT MATCH!")  # debug for no match
            print(f"difference: '{password1}' != '{password2}'")  # debug for difference
            createLabel.config(text="Passwords do not match, try again:")

    # function to check master password
    def checkMasterPassword():
        nonlocal masterPasswordString, passwordsDictionary
        print("=== MASTER PASSWORD CHECK STARTED ===")  # debug for start
        
        # step 1: get entered password
        enteredPassword = loginEntry.get()
        print(f"entered password: '{enteredPassword}'")  # debug for entered password
        print(f"length entered password: {len(enteredPassword)} characters")  # debug for length
        
        # step 2: hash the entered password
        print("entered password will be hashed with sha-256...")  # debug for hashing
        hashedEntered = hashText(enteredPassword)
        print(f"hash of entered password: {hashedEntered}")  # debug for entered hash
        print(f"length hash entered password: {len(hashedEntered)} characters")  # debug for hash length
        
        # step 3: load stored hash from file
        print("stored hash will be loaded from master_password.json...")  # debug for loading
        storedHash = loadMasterPasswordFromFile()
        
        if storedHash is None:
            print("ERROR: no stored hash found!")  # debug for no hash
            loginLabel.config(text="Error loading master password, try again:")
            return
        
        print(f"stored hash from file: {storedHash}")  # debug for stored hash
        print(f"length stored hash: {len(storedHash)} characters")  # debug for stored hash length
        
        # step 4: compare the hashes
        print("comparing hashes...")  # debug for comparing
        print(f"entered hash: {hashedEntered}")  # debug repeat for comparison
        print(f"stored hash:  {storedHash}")  # debug repeat for comparison
        
        if hashedEntered == storedHash:
            print("✓ HASHES MATCH - PASSWORD CORRECT!")  # debug for match
            print("master password accepted, logging in...")  # debug for success
            masterPasswordString = enteredPassword
            print("loading passwords from passwords.json...")  # debug for loading passwords
            passwordsDictionary = loadPasswordsFromFile(masterPasswordString)
            print(f"number of passwords loaded: {len(passwordsDictionary)}")  # debug for password count
            loginFrame.pack_forget()
            mainFrame.pack(pady=20)
            updatePasswords()
            print("=== LOGIN SUCCESSFULLY COMPLETED ===")  # debug for end success
        else:
            print("✗ HASHES DO NOT MATCH - WRONG PASSWORD!")  # debug for no match
            print("difference in hashes:")  # debug for difference
            for i in range(min(len(hashedEntered), len(storedHash))):
                if hashedEntered[i] != storedHash[i]:
                    print(f"  - position {i}: entered='{hashedEntered[i]}', stored='{storedHash[i]}'")  # debug for first difference
                    break
            loginLabel.config(text="Wrong password, try again:")
            print("=== LOGIN FAILED ===")  # debug for end fail
      
    # function to delete master password and all data
    def deleteMasterPasswordAndRestart():
        # ask confirmation
        import tkinter.messagebox as messagebox
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the master password and ALL saved passwords?\n\nThis cannot be undone!"):
            print("deleting master password and data...")  # debug for deletion
            if wipeMasterPasswordAndRestart():
                messagebox.showinfo("Completed", "All data has been wiped. The application will restart.")
                mainWindow.destroy()
                startGuiApplication()
            else:
                messagebox.showerror("Error", "Something went wrong while deleting the files.")

    # function to generate and show password
    def generateAndShowPassword():
        print("=== PASSWORD GENERATION STARTED ===")  # debug for start
        
        # step 1: get length
        lengthText = lengthEntry.get()
        try:
            passwordLength = int(lengthText)
            print(f"desired password length: {passwordLength}")  # debug for length
        except:
            passwordLength = 8
            print("no valid length entered, default length 8 used")  # debug for default
        
        # step 2: get required text
        requiredText = requiredTextEntry.get()
        print(f"required text: '{requiredText}'")  # debug for required text
        print(f"length required text: {len(requiredText)} characters")  # debug for required text length
        
        # step 3: check if password is long enough for required text
        if len(requiredText) > passwordLength:
            print(f"ERROR: required text ({len(requiredText)} characters) is longer than password ({passwordLength} characters)")
            passwordLength = len(requiredText) + 5  # make password longer
            print(f"password length adjusted to: {passwordLength}")
            
        # step 4: build special characters string from checkboxes
        specialCharactersString = ""
        if exclamationVariable.get():
            specialCharactersString += "!"
        if dollarVariable.get():
            specialCharactersString += "$"
        if hashVariable.get():
            specialCharactersString += "#"
        if questionVariable.get():
            specialCharactersString += "?"
        if atVariable.get():
            specialCharactersString += "@"
        if ampersandVariable.get():
            specialCharactersString += "&"
        if asteriskVariable.get():
            specialCharactersString += "*"
        if caretVariable.get():
            specialCharactersString += "^"
        if euroVariable.get():
            specialCharactersString += "€"
        if percentVariable.get():
            specialCharactersString += "%"
        if plusVariable.get():
            specialCharactersString += "+"
        
        print(f"selected special characters: '{specialCharactersString}'")  # debug for special characters
        print(f"use uppercase: {upperCaseVariable.get()}")  # debug for uppercase
        
        # step 5: generate base password
        remainingLength = passwordLength - len(requiredText)
        print(f"remaining length for random characters: {remainingLength}")  # debug for remaining length
        
        if remainingLength > 0:
            basePart = generatePasswordString(specialCharactersString, upperCaseVariable.get(), remainingLength)
            print(f"generated base part: '{basePart}'")  # debug for base part
        else:
            basePart = ""
            print("no room for extra characters")  # debug for no room
        
        # step 6: add required text at random position
        if requiredText:
            # determine where required text goes
            import time
            seedValue = int(time.time() * 1000) % 1000
            insertPosition = seedValue % (len(basePart) + 1)
            print(f"required text will be inserted at position: {insertPosition}")  # debug for position
            
            # insert required text
            finalPassword = basePart[:insertPosition] + requiredText + basePart[insertPosition:]
            print(f"password after adding required text: '{finalPassword}'")  # debug for final
        else:
            finalPassword = basePart
            print("no required text, using base password")  # debug for base only
        
        # step 7: show result
        print(f"final generated password: '{finalPassword}'")  # debug for final
        print(f"final length: {len(finalPassword)} characters")  # debug for final length
        passwordEntry.delete(0, END)
        passwordEntry.insert(0, finalPassword)
        updatePasswordStrengthIndicator()  # update strength indicator after generation
        print("=== PASSWORD GENERATION COMPLETED ===")  # debug for end
    
    # function to add password
    def addPassword():
        siteValue = siteEntry.get()
        usernameValue = usernameEntry.get()
        emailValue = emailEntry.get()
        passwordValue = passwordEntry.get()
        
        if siteValue and passwordValue:
            print("adding password...")  # debug for adding
            # save as dictionary with all fields
            passwordsDictionary[siteValue] = {
                'username': usernameValue,
                'email': emailValue,
                'password': passwordValue
            }
            savePasswordsToFile(passwordsDictionary, masterPasswordString)
            siteEntry.delete(0, END)
            usernameEntry.delete(0, END)
            emailEntry.delete(0, END)
            passwordEntry.delete(0, END)
            updatePasswords()
        else:
            messagebox.showwarning("Warning", "Website name and password are required!")    
    
    # function to show passwords
    def updatePasswords():
        print("updating passwords...")  # debug for update
        updatePasswordList()
    
    # function to update password list
    def updatePasswordList():
        passwordListbox.delete(0, END)
        # sort passwords alphabetically by site name
        sortedPasswordsList = sorted(passwordsDictionary.items())
        for siteValue, passwordData in sortedPasswordsList:
            # check if it's old format (string only) or new format (dictionary)
            if isinstance(passwordData, dict):
                username = passwordData.get('username', '')
                email = passwordData.get('email', '')
                password = passwordData.get('password', '')
                
                # create clear display
                displayText = f"Website: {siteValue}"
                if username:
                    displayText += f" | User: {username}"
                if email:
                    displayText += f" | Email: {email}"
                displayText += f" | Password: {password}"
            else:
                # old format support
                displayText = f"Website: {siteValue} | Password: {passwordData}"
            
            passwordListbox.insert(END, displayText)
    
    # function to edit password
    def editPassword():
        selectionValue = passwordListbox.curselection()
        if selectionValue:
            indexValue = selectionValue[0]
            selectedItemValue = passwordListbox.get(indexValue)
            # extract website name from display text
            siteValue = selectedItemValue.split(" | ")[0].replace("Website: ", "")
            
            currentPasswordData = passwordsDictionary[siteValue]
            
            # check if it's old or new format
            if isinstance(currentPasswordData, dict):
                currentUsername = currentPasswordData.get('username', '')
                currentEmail = currentPasswordData.get('email', '')
                currentPassword = currentPasswordData.get('password', '')
            else:
                # old format
                currentUsername = ''
                currentEmail = ''
                currentPassword = currentPasswordData
            
            # create edit dialog
            editWindow = Tk()
            editWindow.title("Edit Password")
            editWindow.geometry("500x400")
            
            Label(editWindow, text=f"Website: {siteValue}", font=("Arial", 12, "bold")).pack(pady=10)
            
            # username field
            Label(editWindow, text="Username:", font=("Arial", 10, "bold")).pack(pady=5)
            newUsernameEntry = Entry(editWindow, width=50, font=("Arial", 10))
            newUsernameEntry.insert(0, currentUsername)
            newUsernameEntry.pack(pady=5)
            
            # email field
            Label(editWindow, text="Email address:", font=("Arial", 10, "bold")).pack(pady=5)
            newEmailEntry = Entry(editWindow, width=50, font=("Arial", 10))
            newEmailEntry.insert(0, currentEmail)
            newEmailEntry.pack(pady=5)
            
            # password field
            Label(editWindow, text="Password:", font=("Arial", 10, "bold")).pack(pady=5)
            newPasswordEntry = Entry(editWindow, width=50, font=("Arial", 10))
            newPasswordEntry.insert(0, currentPassword)
            newPasswordEntry.pack(pady=5)
            
            def saveEdit():
                newUsername = newUsernameEntry.get()
                newEmail = newEmailEntry.get()
                newPassword = newPasswordEntry.get()
                if newPassword:
                    passwordsDictionary[siteValue] = {
                        'username': newUsername,
                        'email': newEmail,
                        'password': newPassword
                    }
                    savePasswordsToFile(passwordsDictionary, masterPasswordString)
                    updatePasswordList()
                    editWindow.destroy()
                else:
                    messagebox.showwarning("Warning", "Password cannot be empty!")
            
            Button(editWindow, text="Save", command=saveEdit, font=("Arial", 10, "bold"), bg="lightgreen").pack(pady=10)
            Button(editWindow, text="Cancel", command=editWindow.destroy, font=("Arial", 10), bg="lightgray").pack(pady=5)
        else:
            messagebox.showwarning("Warning", "Select a password to edit first.")
    
    # function to delete password
    def deletePassword():
        selectionValue = passwordListbox.curselection()
        if selectionValue:
            indexValue = selectionValue[0]
            selectedItemValue = passwordListbox.get(indexValue)
            # extract website name from display text
            siteValue = selectedItemValue.split(" | ")[0].replace("Website: ", "")
            
            # confirm deletion
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete all data for '{siteValue}'?"):
                del passwordsDictionary[siteValue]
                savePasswordsToFile(passwordsDictionary, masterPasswordString)
                updatePasswordList()
        else:
            messagebox.showwarning("Warning", "Select an item to delete first.")
    
    # function to check password strength
    def checkPasswordStrength(passwordString):
        print(f"checking password strength for: '{passwordString}'")  # debug for strength
        
        # step 1: basic check for length
        if len(passwordString) == 0:
            return 0, "no password", "gray"
        
        strengthScore = 0
        strengthText = ""
        strengthColor = "red"
        
        # step 2: check different criteria
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
            elif character in "!@#$%^&*()_+-=[]{}|;':\",./<>?€":
                hasSpecialChars = True
        
        # step 3: calculate score based on criteria
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
        
        # step 4: determine strength level
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
        
        print(f"strength score: {strengthScore}, level: {strengthText}")  # debug for score
        return strengthScore, strengthText, strengthColor
    
    # function to update strength indicator
    def updatePasswordStrengthIndicator():
        passwordValue = passwordEntry.get()
        score, text, color = checkPasswordStrength(passwordValue)
        strengthLabel.config(text=f"Strength: {text}", fg=color)
        print(f"strength indicator updated: {text} ({color})")  # debug for update

    # Now create buttons with proper commands (after functions are defined)
    createButton = Button(createPasswordFrame, text="Create", font=("Arial", 11, "bold"), bg="lightblue")
    loginButton = Button(loginFrame, text="Login", font=("Arial", 11, "bold"), bg="lightgreen")
    deleteMasterButton = Button(loginFrame, text="Wipe All Data", font=("Arial", 10, "bold"), bg="red", fg="white")
    # Simple button state tracking to prevent double clicks
    button_enabled = True
    def disable_buttons_temporarily():
        nonlocal button_enabled
        button_enabled = False
        def reset_button_state():
            nonlocal button_enabled
            button_enabled = True
        mainWindow.after(1000, reset_button_state)
    
    def safe_create():
        nonlocal button_enabled
        if button_enabled:
            disable_buttons_temporarily()
            createNewMasterPassword()
    
    def safe_login():
        nonlocal button_enabled
        if button_enabled:
            disable_buttons_temporarily()
            checkMasterPassword()
    
    def safe_delete():
        nonlocal button_enabled
        if button_enabled:
            disable_buttons_temporarily()
            deleteMasterPasswordAndRestart()
    
    def safe_generate():
        nonlocal button_enabled
        if button_enabled:
            disable_buttons_temporarily()
            generateAndShowPassword()
    
    def safe_add():
        nonlocal button_enabled
        if button_enabled:
            disable_buttons_temporarily()
            addPassword()
    
    def safe_edit():
        nonlocal button_enabled
        if button_enabled:
            disable_buttons_temporarily()
            editPassword()
    
    def safe_delete_password():
        nonlocal button_enabled
        if button_enabled:
            disable_buttons_temporarily()
            deletePassword()
    
    def safe_refresh():
        nonlocal button_enabled
        if button_enabled:
            disable_buttons_temporarily()
            updatePasswordList()
    
    # Assign commands
    createButton.config(command=safe_create)
    loginButton.config(command=safe_login)
    deleteMasterButton.config(command=safe_delete)
    generateButton.config(command=safe_generate)
    addButton.config(command=safe_add)
    editButton.config(command=safe_edit)
    deleteButton.config(command=safe_delete_password)
    refreshButton.config(command=safe_refresh)    # decide which frame to show
    if not checkIfMasterPasswordIsSet():
        print("no valid master password found, show creation screen...")  # debug
        createLabel.pack(pady=5)
        createEntry.pack(pady=5)
        confirmLabel.pack(pady=5)
        confirmEntry.pack(pady=5)
        createButton.pack(pady=5)
        createPasswordFrame.pack(pady=20)
    else:
        print("valid master password found, show login screen...")  # debug
        loginLabel.pack(pady=5)
        loginEntry.pack(pady=5)
        loginButton.pack(pady=5)
        deleteMasterButton.pack(pady=5)
        loginFrame.pack(pady=20)
    
    # pack left frame elements - COMPACT LAYOUT
    # website info frame
    siteLabel.pack(pady=2)
    siteEntry.pack(pady=2)
    usernameLabel.pack(pady=2)
    usernameEntry.pack(pady=2)
    emailLabel.pack(pady=2)
    emailEntry.pack(pady=2)
    websiteInfoFrame.pack(pady=5, fill="x")
    
    # password info frame
    passwordLabel.pack(pady=2)
    passwordEntry.pack(pady=2)
    strengthLabel.pack(pady=2)
    passwordInfoFrame.pack(pady=5, fill="x")
    
    # pack special characters - COMPACT
    # Row 1
    exclamationCheck.pack(side=LEFT, padx=2)
    dollarCheck.pack(side=LEFT, padx=2)
    hashCheck.pack(side=LEFT, padx=2)
    questionCheck.pack(side=LEFT, padx=2)
    atCheck.pack(side=LEFT, padx=2)
    specialRow1.pack(pady=2)
    
    # Row 2
    ampersandCheck.pack(side=LEFT, padx=2)
    asteriskCheck.pack(side=LEFT, padx=2)
    caretCheck.pack(side=LEFT, padx=2)
    euroCheck.pack(side=LEFT, padx=2)
    percentCheck.pack(side=LEFT, padx=2)
    plusCheck.pack(side=LEFT, padx=2)
    specialRow2.pack(pady=2)
    
    specialCharsFrame.pack(pady=3, fill="x")
    
    # Other options
    upperCaseCheck.pack(side=LEFT, padx=5)
    lengthFrame.pack(side=LEFT, padx=5)
    lengthLabel.pack(side=LEFT)
    lengthEntry.pack(side=LEFT)
    otherOptionsFrame.pack(pady=5, fill="x")
    
    requiredFrame.pack(pady=5, fill="x")
    requiredTextLabel.pack(side=LEFT)
    requiredTextEntry.pack(side=LEFT, expand=True, fill="x")
    
    specialFrame.pack(pady=5, fill="x")
    
    # action buttons frame
    generateButton.pack(side=LEFT, padx=10, expand=True, fill="x")
    addButton.pack(side=LEFT, padx=10, expand=True, fill="x")
    buttonActionsFrame.pack(pady=5, fill="x")
    
    # pack right frame elements
    listLabel.pack(pady=5)
    passwordListbox.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    listFrame.pack(fill=BOTH, expand=True, pady=5)
    
    editButton.pack(side=LEFT, padx=5)
    deleteButton.pack(side=LEFT, padx=5)
    refreshButton.pack(side=LEFT, padx=5)
    buttonFrame.pack(pady=5)
    
    # pack main frames
    leftFrame.pack(side=LEFT, fill=Y, padx=20, pady=20)
    rightFrame.pack(side=RIGHT, fill=BOTH, expand=True, padx=20, pady=20)
    
    # bind Enter key to login and create buttons for better UX
    def onEnterPressed(event):
        if loginFrame.winfo_viewable():
            checkMasterPassword()
        elif createPasswordFrame.winfo_viewable():
            createNewMasterPassword()
    
    mainWindow.bind('<Return>', onEnterPressed)
    
    # start mainloop
    print("starting mainloop...")  # debug for mainloop
    mainWindow.mainloop()

# start the gui
print("script started...")  # debug to check if script begins
startGuiApplication()