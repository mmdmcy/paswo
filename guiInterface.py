from tkinter import Tk, Toplevel, Frame, Label, Entry, Button, Checkbutton, IntVar, END, Listbox, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH, messagebox
import secrets
from encryption import VaultError, WrongPasswordOrTampered
from fileHandler import (savePasswordsToFile, loadPasswordsFromFile, vaultExists,
                         legacyVaultExists, migrateLegacyVault, wipeVault, getVaultPath)
from passwordGenerator import generatePasswordString

# NOTE: the master password is never written to disk, hashed into a side
# file, or printed. The only proof of it is that the vault decrypts.

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
        
        # step 1: get passwords
        password1 = createEntry.get()
        password2 = confirmEntry.get()
        
        # step 2: check if both passwords are filled
        if not password1:
            createLabel.config(text="Password cannot be empty:")
            return
        
        if not password2:
            createLabel.config(text="Confirmation cannot be empty:")
            return
        
        # step 3: check if passwords match
        if password1 != password2:
            createLabel.config(text="Passwords do not match, try again:")
            return
        
        # step 4: create the (empty) vault; the file itself proves the password later
        try:
            savePasswordsToFile({}, password1)
        except OSError as error:
            messagebox.showerror("Error", f"Could not create the vault:\n{error}")
            return
        masterPasswordString = password1
        passwordsDictionary = {}
        createEntry.delete(0, END)
        confirmEntry.delete(0, END)
        createPasswordFrame.pack_forget()
        mainFrame.pack(pady=20)
        updatePasswords()

    # function to check master password
    def checkMasterPassword():
        nonlocal masterPasswordString, passwordsDictionary
        
        # step 1: get entered password
        enteredPassword = loginEntry.get()
        if not enteredPassword:
            loginLabel.config(text="Password cannot be empty:")
            return
        
        # step 2: decrypt the vault; success is the password check
        try:
            if vaultExists():
                loadedPasswords = loadPasswordsFromFile(enteredPassword)
            else:
                # old paswo 1.0 files found: migrate them once to the new format
                loadedPasswords = migrateLegacyVault(enteredPassword)
                messagebox.showinfo(
                    "Vault upgraded",
                    "Your old vault was upgraded to the new encrypted format and is now stored at:\n"
                    f"{getVaultPath()}\n\n"
                    "The old files were moved to a legacy-backup folder next to it. "
                    "They are protected only by the old, weak cipher: delete them once "
                    "you have checked that all your entries are present.")
        except WrongPasswordOrTampered:
            loginLabel.config(text="Wrong password, try again:")
            return
        except VaultError as error:
            messagebox.showerror("Vault error", f"The vault could not be read:\n{error}")
            return
        except OSError as error:
            messagebox.showerror("Error", f"Could not open the vault:\n{error}")
            return
        
        masterPasswordString = enteredPassword
        passwordsDictionary = loadedPasswords
        loginEntry.delete(0, END)
        loginFrame.pack_forget()
        mainFrame.pack(pady=20)
        updatePasswords()
      
    # function to delete master password and all data
    def deleteMasterPasswordAndRestart():
        # ask confirmation
        import tkinter.messagebox as messagebox
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the master password and ALL saved passwords?\n\nThis cannot be undone!"):
            if wipeVault():
                messagebox.showinfo("Completed", "All data has been wiped. The application will restart.")
                mainWindow.destroy()
                startGuiApplication()
            else:
                messagebox.showerror("Error", "Something went wrong while deleting the files.")

    # function to generate and show password
    def generateAndShowPassword():
        
        # step 1: get length
        lengthText = lengthEntry.get()
        try:
            passwordLength = int(lengthText)
        except:
            passwordLength = 8
        
        # step 2: get required text
        requiredText = requiredTextEntry.get()
        
        # step 3: check if password is long enough for required text
        if len(requiredText) > passwordLength:
            passwordLength = len(requiredText) + 5  # make password longer
            
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
        
        
        # step 5: generate base password
        remainingLength = passwordLength - len(requiredText)
        
        if remainingLength > 0:
            basePart = generatePasswordString(specialCharactersString, upperCaseVariable.get(), remainingLength)
        else:
            basePart = ""
        
        # step 6: add required text at random position
        if requiredText:
            # determine where required text goes
            insertPosition = secrets.randbelow(len(basePart) + 1)
            
            # insert required text
            finalPassword = basePart[:insertPosition] + requiredText + basePart[insertPosition:]
        else:
            finalPassword = basePart
        
        # step 7: show result
        passwordEntry.delete(0, END)
        passwordEntry.insert(0, finalPassword)
        updatePasswordStrengthIndicator()  # update strength indicator after generation
    
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
            editWindow = Toplevel(mainWindow)
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
        
        return strengthScore, strengthText, strengthColor
    
    # function to update strength indicator
    def updatePasswordStrengthIndicator():
        passwordValue = passwordEntry.get()
        score, text, color = checkPasswordStrength(passwordValue)
        strengthLabel.config(text=f"Strength: {text}", fg=color)

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
    if not vaultExists() and not legacyVaultExists():
        createLabel.pack(pady=5)
        createEntry.pack(pady=5)
        confirmLabel.pack(pady=5)
        confirmEntry.pack(pady=5)
        createButton.pack(pady=5)
        createPasswordFrame.pack(pady=20)
    else:
        if not vaultExists():
            loginLabel.config(text="Old vault found. Enter your master password to upgrade it:")
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