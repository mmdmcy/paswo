from tkinter import Tk, Frame, Label, Entry, Button, Checkbutton, IntVar, END, Listbox, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH, messagebox, ttk, StringVar, Toplevel, X, Menu
from encryption import hashText
from fileHandler import savePasswordsToFile, loadPasswordsFromFile
from passwordGenerator import generatePasswordString

# =================================================================
# Utility Functions
# =================================================================

def checkIfFileExists(fileNameString):
    print(f"checking if file exists: {fileNameString}")  # debug for file
    try:
        fileHandle = open(fileNameString, 'r')
        fileHandle.close()
        return True
    except:
        return False

def checkIfMasterPasswordIsSet():
    print("checking if master password is actually set...")  # debug
    try:
        if not checkIfFileExists('master_password.json'):
            print("master_password.json does not exist")  # debug
            return False
        
        hashedPassword = loadMasterPasswordFromFile()
        
        if hashedPassword is None or hashedPassword == "":
            print("no valid hash found in master_password.json")  # debug
            return False
        
        print(f"valid hash found: {hashedPassword[:10]}...")  # debug
        return True
    except:
        print("error checking master password status")  # debug
        return False

def saveMasterPasswordToFile(masterPasswordString):
    print("hashing and saving master password to json...")  # debug for saving
    hashedPasswordString = hashText(masterPasswordString)
    
    jsonString = "{\n"
    jsonString = jsonString + '  "master_password_hash": "'
    jsonString = jsonString + hashedPasswordString
    jsonString = jsonString + '"\n'
    jsonString = jsonString + "}"
    
    fileHandle = open('master_password.json', 'w')
    fileHandle.write(jsonString)
    fileHandle.close()
    print("master password saved to master_password.json")  # debug for location

def loadMasterPasswordFromFile():
    print("loading master password from json...")  # debug for loading
    try:
        if not checkIfFileExists('master_password.json'):
            return None
        
        fileHandle = open('master_password.json', 'r')
        jsonContent = fileHandle.read()
        fileHandle.close()
        
        cleanContent = jsonContent.strip()
        
        if cleanContent.startswith('{'):
            cleanContent = cleanContent[1:]
        if cleanContent.endswith('}'):
            cleanContent = cleanContent[:-1]
        
        if '"master_password_hash":' in cleanContent:
            colonPosition = cleanContent.find(':')
            firstQuote = cleanContent.find('"', colonPosition)
            secondQuote = cleanContent.find('"', firstQuote + 1)
            
            if firstQuote != -1 and secondQuote != -1:
                hashedPassword = cleanContent[firstQuote + 1:secondQuote]
                return hashedPassword
        
        return None
    except:
        return None

def wipeMasterPasswordAndRestart():
    print("wiping all password data...")  # debug for wiping
    
    emptyMasterJson = "{\n"
    emptyMasterJson = emptyMasterJson + '  "master_password_hash": ""\n'
    emptyMasterJson = emptyMasterJson + "}"
    
    try:
        fileHandle = open('master_password.json', 'w')
        fileHandle.write(emptyMasterJson)
        fileHandle.close()
        print("master_password.json wiped")
    except:
        print("error wiping master_password.json")
    
    emptyPasswordsJson = "{}"
    
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
    mainWindow = Tk()
    print("setting window title...")  # debug after window creation
    
    # =================================================================
    # Variables
    # =================================================================
    masterPasswordString = ''
    passwordsDictionary = {}
    
    # Special character variables
    exclamationVariable = IntVar(value=1)
    dollarVariable = IntVar(value=1)
    hashVariable = IntVar(value=1)
    questionVariable = IntVar(value=1)
    atVariable = IntVar(value=1)
    ampersandVariable = IntVar(value=1)
    asteriskVariable = IntVar(value=1)
    caretVariable = IntVar(value=1)
    euroVariable = IntVar(value=1)
    percentVariable = IntVar(value=1)
    plusVariable = IntVar(value=1)
    upperCaseVariable = IntVar(value=1)
    dashesVariable = IntVar(value=0)
    excludeSimilarVariable = IntVar(value=0)

    # New complexity requirements
    require_2_upper_var = IntVar(value=1)
    require_2_digits_var = IntVar(value=1)
    require_2_special_var = IntVar(value=1)

    # StringVars for entry fields to be shared with advanced window
    length_var = StringVar(value="12")
    required_text_var = StringVar(value="")
    exclude_chars_var = StringVar(value="")

    # =================================================================
    # UI Creation
    # =================================================================

    # --- Main Window ---
    mainWindow.title("Paswo - Password Manager")
    mainWindow.geometry("1400x800")
    
    # --- Paned Window for Resizable Layout ---
    paned_window = ttk.PanedWindow(mainWindow, orient='horizontal')
    paned_window.pack(fill=BOTH, expand=True)

    # =================================================================
    # Left Frame (Password Generation & Adding)
    # =================================================================
    leftFrame = Frame(paned_window, width=450, padx=10, pady=10)
    paned_window.add(leftFrame, weight=1)

    # --- Right Frame (Password List) ---
    rightFrame = Frame(paned_window, padx=10, pady=10)
    paned_window.add(rightFrame, weight=3)


    # =================================================================
    # Core Functions
    # =================================================================
    
    def createNewMasterPassword(*args):
        nonlocal masterPasswordString, passwordsDictionary
        password1 = createEntry.get()
        password2 = confirmEntry.get()
        
        if not password1:
            createLabel.config(text="Password cannot be empty:")
            return
        
        if not password2:
            createLabel.config(text="Confirmation cannot be empty:")
            return
        
        if password1 == password2:
            masterPasswordString = password1
            saveMasterPasswordToFile(masterPasswordString)
            createPasswordFrame.pack_forget()
            paned_window.pack(fill=BOTH, expand=True)
            updatePasswords()
        else:
            createLabel.config(text="Passwords do not match, try again:")

    def checkMasterPassword(*args):
        nonlocal masterPasswordString, passwordsDictionary
        enteredPassword = loginEntry.get()
        hashedEntered = hashText(enteredPassword)
        storedHash = loadMasterPasswordFromFile()
        
        if storedHash is None:
            loginLabel.config(text="Error loading master password, try again:")
            return
        
        if hashedEntered == storedHash:
            masterPasswordString = enteredPassword
            try:
                passwordsDictionary = loadPasswordsFromFile(masterPasswordString)
                if passwordsDictionary is None:
                    passwordsDictionary = {}
            except Exception as e:
                print(f"Error loading passwords: {str(e)}")
                passwordsDictionary = {}
            
            loginFrame.pack_forget()
            paned_window.pack(fill=BOTH, expand=True)
            updatePasswords()
        else:
            loginLabel.config(text="Wrong password, try again:")

    def deleteMasterPasswordAndRestart():
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the master password and ALL saved passwords?\n\nThis cannot be undone!"):
            if wipeMasterPasswordAndRestart():
                messagebox.showinfo("Completed", "All data has been wiped. The application will restart.")
                mainWindow.destroy()
                startGuiApplication()
            else:
                messagebox.showerror("Error", "Something went wrong while deleting the files.")

    def generateAndShowPassword():
        try:
            passwordLength = int(length_var.get())
        except:
            passwordLength = 12
        
        requiredText = required_text_var.get()
        
        if len(requiredText) > passwordLength:
            passwordLength = len(requiredText) + 4
        
        specialCharactersString = ""
        if exclamationVariable.get(): specialCharactersString += "!"
        if dollarVariable.get(): specialCharactersString += "$"
        if hashVariable.get(): specialCharactersString += "#"
        if questionVariable.get(): specialCharactersString += "?"
        if atVariable.get(): specialCharactersString += "@"
        if ampersandVariable.get(): specialCharactersString += "&"
        if asteriskVariable.get(): specialCharactersString += "*"
        if caretVariable.get(): specialCharactersString += "^"
        if euroVariable.get(): specialCharactersString += "€"
        if percentVariable.get(): specialCharactersString += "%"
        if plusVariable.get(): specialCharactersString += "+"
        
        remainingLength = passwordLength - len(requiredText)
        
        # This part remains the same, it just reads the vars
        if remainingLength > 0:
            excludedChars = exclude_chars_var.get()
            basePart = generatePasswordString(
                specialCharactersString, 
                upperCaseVariable.get(), 
                remainingLength,
                excludeSimilarVariable.get(),
                excludedChars,
                require_2_upper_var.get(),
                require_2_digits_var.get(),
                require_2_special_var.get()
            )
        else:
            basePart = ""
        
        if requiredText:
            import time
            seedValue = int(time.time() * 1000) % 1000
            insertPosition = seedValue % (len(basePart) + 1)
            finalPassword = basePart[:insertPosition] + requiredText + basePart[insertPosition:]
        else:
            finalPassword = basePart
        
        if dashesVariable.get() and len(finalPassword) > 0:
            finalPassword = '-'.join(finalPassword[i:i+4] for i in range(0, len(finalPassword), 4))
        
        passwordEntry.delete(0, END)
        passwordEntry.insert(0, finalPassword)
        updatePasswordStrengthIndicator()

    def toggle_advanced_options():
        if advanced_options_frame.winfo_viewable():
            advanced_options_frame.pack_forget()
            advancedButton.config(text="Advanced...")
        else:
            advanced_options_frame.pack(after=buttonActionsFrame, pady=10, fill='x')
            advancedButton.config(text="Hide Advanced")

    def addPassword():
        siteValue = siteEntry.get()
        usernameValue = usernameEntry.get()
        emailValue = emailEntry.get()
        passwordValue = passwordEntry.get()
        
        if siteValue and passwordValue:
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

    def updatePasswords():
        searchEntry.delete(0, END)
        updatePasswordList()

    def updatePasswordList(passwords_to_show=None):
        passwordTree.delete(*passwordTree.get_children())
        if passwords_to_show is None:
            passwords_to_show = passwordsDictionary
        sortedPasswordsList = sorted(passwords_to_show.items())
        
        # Add data to the treeview with alternating row colors
        for i, (siteValue, passwordData) in enumerate(sortedPasswordsList):
            tag = 'oddrow' if i % 2 else 'evenrow'
            if isinstance(passwordData, dict):
                username = passwordData.get('username', '') or 'N/A'
                email = passwordData.get('email', '') or 'N/A'
                passwordTree.insert('', END, values=(siteValue, username, email, '********'), tags=(tag,))
            else:
                # old format support
                passwordTree.insert('', END, values=(siteValue, 'N/A', 'N/A', '********'), tags=(tag,))

    def searchPasswords(*args):
        searchTerm = searchEntry.get().lower()
        search_filter = searchFilterVar.get()

        if not searchTerm:
            updatePasswordList()
            return
        
        filteredPasswords = {}
        for site, data in passwordsDictionary.items():
            if isinstance(data, dict):
                website = site.lower()
                username = data.get('username', '').lower()
                email = data.get('email', '').lower()

                if search_filter == "All" and (searchTerm in website or searchTerm in username or searchTerm in email):
                    filteredPasswords[site] = data
                elif search_filter == "Website" and searchTerm in website:
                    filteredPasswords[site] = data
                elif search_filter == "Username" and searchTerm in username:
                    filteredPasswords[site] = data
                elif search_filter == "Email" and searchTerm in email:
                    filteredPasswords[site] = data
        updatePasswordList(filteredPasswords)

    def treeview_sort_column(tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

    def on_double_click(event):
        item_id = passwordTree.identify_row(event.y)
        if item_id:
            item_values = passwordTree.item(item_id, 'values')
            siteValue = item_values[0]
            show_details_window(siteValue)

    def show_details_window(siteValue):
        details = passwordsDictionary.get(siteValue)
        if not details:
            return

        details_window = Toplevel(mainWindow)
        details_window.title("Entry Details")
        details_window.geometry("600x250")
        details_window.resizable(False, False)
        details_window.transient(mainWindow)
        details_window.grab_set()

        main_frame = Frame(details_window, padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)

        # Helper function for creating rows
        def create_detail_row(parent, label_text, value_text, is_password=False):
            row_frame = Frame(parent)
            
            label = Label(row_frame, text=f"{label_text}:", font=("Arial", 10, "bold"), width=12, anchor='w')
            label.pack(side=LEFT, padx=(0, 5))

            entry_var = StringVar(value=value_text)
            entry = Entry(row_frame, textvariable=entry_var, font=("Arial", 10), state='readonly', relief='flat', readonlybackground='white')
            entry.pack(side=LEFT, fill=X, expand=True)

            def copy_to_clipboard():
                mainWindow.clipboard_clear()
                mainWindow.clipboard_append(value_text)
                messagebox.showinfo("Copied", f"{label_text} copied to clipboard.", parent=details_window)

            copy_button = Button(row_frame, text="Copy", width=8, command=copy_to_clipboard)
            copy_button.pack(side=LEFT, padx=5)
            
            if is_password:
                entry.config(show='*')
                def toggle_password():
                    if entry.cget('show') == '*':
                        entry.config(show='')
                        show_button.config(text="Hide")
                    else:
                        entry.config(show='*')
                        show_button.config(text="Show")
                show_button = Button(row_frame, text="Show", width=8, command=toggle_password)
                show_button.pack(side=LEFT, padx=(0, 5))
            
            row_frame.pack(fill=X, pady=4)

        # Create rows for each detail
        create_detail_row(main_frame, "Website", siteValue)
        create_detail_row(main_frame, "Username", details.get('username', 'N/A'))
        create_detail_row(main_frame, "Email", details.get('email', 'N/A'))
        create_detail_row(main_frame, "Password", details.get('password', ''), is_password=True)

        close_button = Button(main_frame, text="Close", command=details_window.destroy, font=("Arial", 10, "bold"), bg="lightgray")
        close_button.pack(pady=(20, 0))

    def copy_from_selection(field_to_copy):
        selected_item = passwordTree.focus()
        if selected_item:
            item_values = passwordTree.item(selected_item, 'values')
            siteValue = item_values[0]
            passwordData = passwordsDictionary.get(siteValue)
            
            if passwordData:
                value_to_copy = ""
                if field_to_copy == 'username':
                    value_to_copy = passwordData.get('username', '')
                elif field_to_copy == 'email':
                    value_to_copy = passwordData.get('email', '')
                elif field_to_copy == 'password':
                    value_to_copy = passwordData.get('password', '')
                
                if value_to_copy and value_to_copy != 'N/A':
                    mainWindow.clipboard_clear()
                    mainWindow.clipboard_append(value_to_copy)
                    print(f"Copied {field_to_copy} for {siteValue}")
                else:
                    print(f"No {field_to_copy} to copy for {siteValue}")

    def view_details_from_menu():
        selected_item = passwordTree.focus()
        if selected_item:
            item_values = passwordTree.item(selected_item, 'values')
            siteValue = item_values[0]
            show_details_window(siteValue)

    def editPassword():
        selected_item = passwordTree.focus()
        if selected_item:
            item_values = passwordTree.item(selected_item, 'values')
            siteValue = item_values[0]
            currentPasswordData = passwordsDictionary[siteValue]
            
            if isinstance(currentPasswordData, dict):
                currentUsername = currentPasswordData.get('username', '')
                currentEmail = currentPasswordData.get('email', '')
                currentPassword = currentPasswordData.get('password', '')
            else:
                currentUsername = ''
                currentEmail = ''
                currentPassword = currentPasswordData
            
            editWindow = Tk()
            editWindow.title("Edit Password")
            editWindow.geometry("500x400")
            
            Label(editWindow, text=f"Website: {siteValue}", font=("Arial", 12, "bold")).pack(pady=10)
            
            Label(editWindow, text="Username:", font=("Arial", 10, "bold")).pack(pady=5)
            newUsernameEntry = Entry(editWindow, width=50, font=("Arial", 10))
            newUsernameEntry.insert(0, currentUsername)
            newUsernameEntry.pack(pady=5)
            
            Label(editWindow, text="Email address:", font=("Arial", 10, "bold")).pack(pady=5)
            newEmailEntry = Entry(editWindow, width=50, font=("Arial", 10))
            newEmailEntry.insert(0, currentEmail)
            newEmailEntry.pack(pady=5)
            
            Label(editWindow, text="Password:", font=("Arial", 10, "bold")).pack(pady=5)
            newPasswordEntry = Entry(editWindow, width=50, font=("Arial", 10))
            newPasswordEntry.insert(0, currentPassword)
            newPasswordEntry.pack(pady=5)
            
            def saveEdit():
                newPassword = newPasswordEntry.get()
                if newPassword:
                    passwordsDictionary[siteValue] = {
                        'username': newUsernameEntry.get(),
                        'email': newEmailEntry.get(),
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

    def deletePassword():
        selected_item = passwordTree.focus()
        if selected_item:
            item_values = passwordTree.item(selected_item, 'values')
            siteValue = item_values[0]
            
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete all data for '{siteValue}'?"):
                del passwordsDictionary[siteValue]
                savePasswordsToFile(passwordsDictionary, masterPasswordString)
                updatePasswordList()
        else:
            messagebox.showwarning("Warning", "Select an item to delete first.")

    def checkPasswordStrength(passwordString):
        if len(passwordString) == 0:
            return 0, "no password", "gray"
        
        strengthScore = 0
        
        if len(passwordString) >= 8: strengthScore += 2
        if len(passwordString) >= 12: strengthScore += 1
        if any(c.islower() for c in passwordString): strengthScore += 1
        if any(c.isupper() for c in passwordString): strengthScore += 1
        if any(c.isdigit() for c in passwordString): strengthScore += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?€" for c in passwordString): strengthScore += 2
        
        if strengthScore >= 7:
            return strengthScore, "very strong", "green"
        elif strengthScore >= 5:
            return strengthScore, "strong", "orange"
        elif strengthScore >= 3:
            return strengthScore, "moderate", "yellow"
        else:
            return strengthScore, "weak", "red"

    def updatePasswordStrengthIndicator():
        passwordValue = passwordEntry.get()
        score, text, color = checkPasswordStrength(passwordValue)
        strengthLabel.config(text=f"Strength: {text}", fg=color)

    # =================================================================
    # UI Elements (Left Frame)
    # =================================================================
    
    # Create Password Frame
    createPasswordFrame = Frame(mainWindow)
    createLabel = Label(createPasswordFrame, text="Create new master password:")
    createEntry = Entry(createPasswordFrame, show="*")
    confirmLabel = Label(createPasswordFrame, text="Confirm master password:")
    confirmEntry = Entry(createPasswordFrame, show="*")
    createButton = Button(createPasswordFrame, text="Create", font=("Arial", 11, "bold"), bg="lightblue", command=createNewMasterPassword)
    
    # Login Frame
    loginFrame = Frame(mainWindow)
    loginLabel = Label(loginFrame, text="Master password:")
    loginEntry = Entry(loginFrame, show="*")
    loginButton = Button(loginFrame, text="Login", font=("Arial", 11, "bold"), bg="lightgreen", command=checkMasterPassword)
    deleteMasterButton = Button(loginFrame, text="Reset All Data", font=("Arial", 10, "bold"), bg="lightcoral", width=15, command=deleteMasterPasswordAndRestart)
    
    # Main Frame
    mainFrame = Frame(mainWindow)
    
    # Website Info Frame
    websiteInfoFrame = Frame(leftFrame, relief="solid", bd=1, padx=10, pady=10)
    Label(websiteInfoFrame, text="Website Information", font=("Arial", 12, "bold")).pack(pady=(0, 5))
    siteLabel = Label(websiteInfoFrame, text="Website name:", font=("Arial", 10, "bold"))
    siteEntry = Entry(websiteInfoFrame, width=30, font=("Arial", 10))
    usernameLabel = Label(websiteInfoFrame, text="Username:", font=("Arial", 10, "bold"))
    usernameEntry = Entry(websiteInfoFrame, width=30, font=("Arial", 10))
    emailLabel = Label(websiteInfoFrame, text="Email address:", font=("Arial", 10, "bold"))
    emailEntry = Entry(websiteInfoFrame, width=30, font=("Arial", 10))
    
    # Password Info Frame
    passwordInfoFrame = Frame(leftFrame, relief="solid", bd=1, padx=10, pady=10)
    Label(passwordInfoFrame, text="Generated Password", font=("Arial", 12, "bold")).pack(pady=(0, 5))
    passwordLabel = Label(passwordInfoFrame, text="Password:", font=("Arial", 10, "bold"))
    passwordEntry = Entry(passwordInfoFrame, width=30, font=("Arial", 10))
    strengthLabel = Label(passwordInfoFrame, text="Strength: no password", fg="gray", font=("Arial", 9))
    
    def copy_generated_password():
        password = passwordEntry.get()
        if password:
            mainWindow.clipboard_clear()
            mainWindow.clipboard_append(password)
            messagebox.showinfo("Copied", "Generated password copied to clipboard.")

    copyGenPassButton = Button(passwordInfoFrame, text="Copy", command=copy_generated_password)

    # Action Buttons Frame
    buttonActionsFrame = Frame(leftFrame) # No border for this one
    generateButton = Button(buttonActionsFrame, text="Generate", font=("Arial", 11, "bold"), bg="lightblue", command=generateAndShowPassword)
    advancedButton = Button(buttonActionsFrame, text="Advanced...", font=("Arial", 11), command=toggle_advanced_options)
    
    # --- Advanced Options Frame (Initially hidden) ---
    advanced_options_frame = Frame(leftFrame, relief="solid", bd=1, padx=10, pady=10)
    
    specialFrame = Frame(advanced_options_frame)
    Label(specialFrame, text="Special chars:", font=("Arial", 10, "bold")).pack(anchor="w")
    specialRow1 = Frame(specialFrame)
    Checkbutton(specialRow1, text="!", variable=exclamationVariable).pack(side=LEFT)
    Checkbutton(specialRow1, text="$", variable=dollarVariable).pack(side=LEFT)
    Checkbutton(specialRow1, text="#", variable=hashVariable).pack(side=LEFT)
    Checkbutton(specialRow1, text="?", variable=questionVariable).pack(side=LEFT)
    Checkbutton(specialRow1, text="@", variable=atVariable).pack(side=LEFT)
    specialRow1.pack(fill='x')
    
    specialRow2 = Frame(specialFrame)
    Checkbutton(specialRow2, text="&", variable=ampersandVariable).pack(side=LEFT)
    Checkbutton(specialRow2, text="*", variable=asteriskVariable).pack(side=LEFT)
    Checkbutton(specialRow2, text="^", variable=caretVariable).pack(side=LEFT)
    Checkbutton(specialRow2, text="€", variable=euroVariable).pack(side=LEFT)
    Checkbutton(specialRow2, text="%", variable=percentVariable).pack(side=LEFT)
    Checkbutton(specialRow2, text="+", variable=plusVariable).pack(side=LEFT)
    specialRow2.pack(fill='x')
    specialFrame.pack(pady=5, fill="x")

    otherOptionsFrame = Frame(advanced_options_frame)
    Checkbutton(otherOptionsFrame, text="Uppercase", variable=upperCaseVariable, font=("Arial", 10)).pack(side=LEFT, padx=5)
    lengthFrame = Frame(otherOptionsFrame)
    Label(lengthFrame, text="Length:", font=("Arial", 10)).pack(side=LEFT)
    Entry(lengthFrame, width=5, font=("Arial", 10), textvariable=length_var).pack(side=LEFT)
    lengthFrame.pack(side=LEFT, padx=10)
    otherOptionsFrame.pack(pady=5, fill="x")

    requiredFrame = Frame(advanced_options_frame)
    Label(requiredFrame, text="Required text:", font=("Arial", 10)).pack(side=LEFT)
    Entry(requiredFrame, width=20, font=("Arial", 10), bg="lightyellow", textvariable=required_text_var).pack(side=LEFT, fill=X, expand=True)
    requiredFrame.pack(pady=5, fill="x")

    customizationFrame = Frame(advanced_options_frame)
    Checkbutton(customizationFrame, text="Add dashes every 4 chars", variable=dashesVariable).pack(anchor="w")
    Checkbutton(customizationFrame, text="Exclude similar chars (I,l,1,O,0)", variable=excludeSimilarVariable).pack(anchor="w")
    customizationFrame.pack(pady=5, fill="x")
    
    excludeCharsFrame = Frame(advanced_options_frame)
    Label(excludeCharsFrame, text="Exclude specific chars:", font=("Arial", 10)).pack(anchor="w")
    Entry(excludeCharsFrame, width=30, font=("Arial", 10), textvariable=exclude_chars_var).pack(fill="x", expand=True)
    excludeCharsFrame.pack(pady=5, fill="x")
    
    complexityFrame = Frame(advanced_options_frame)
    Label(complexityFrame, text="Complexity Rules:", font=("Arial", 10, "bold")).pack(anchor="w")
    Checkbutton(complexityFrame, text="Require 2+ Uppercase", variable=require_2_upper_var).pack(anchor="w")
    Checkbutton(complexityFrame, text="Require 2+ Digits", variable=require_2_digits_var).pack(anchor="w")
    Checkbutton(complexityFrame, text="Require 2+ Special Chars", variable=require_2_special_var).pack(anchor="w")
    complexityFrame.pack(pady=5, fill="x")

    addButton = Button(leftFrame, text="Add Entry to List", font=("Arial", 11, "bold"), bg="lightgreen", command=addPassword)

    # =================================================================
    # UI Elements (Right Frame)
    # =================================================================
    
    listLabel = Label(rightFrame, text="Saved Passwords:", font=("Arial", 12, "bold"))
    
    # Search Frame
    searchFrame = Frame(rightFrame)
    Label(searchFrame, text="Search:", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)
    searchEntry = Entry(searchFrame, width=40, font=("Arial", 10))
    searchButton = Button(searchFrame, text="Search", font=("Arial", 10, "bold"), command=searchPasswords)
    searchFilterVar = StringVar(value="All")
    searchFilter = ttk.Combobox(searchFrame, textvariable=searchFilterVar, values=["All", "Website", "Username", "Email"], width=10, state="readonly")
    
    # List Frame
    listFrame = Frame(rightFrame)
    v_scrollbar = Scrollbar(listFrame, orient=VERTICAL)
    h_scrollbar = Scrollbar(listFrame, orient='horizontal')
    passwordTree = ttk.Treeview(listFrame, columns=('website', 'username', 'email', 'password'), show='headings', yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    v_scrollbar.config(command=passwordTree.yview)
    h_scrollbar.config(command=passwordTree.xview)

    # Define columns
    passwordTree.heading('website', text='Website')
    passwordTree.heading('username', text='Username')
    passwordTree.heading('email', text='Email')
    passwordTree.heading('password', text='Password')
    passwordTree.column('website', width=200, minwidth=150)
    passwordTree.column('username', width=200, minwidth=150)
    passwordTree.column('email', width=250, minwidth=200)
    passwordTree.column('password', width=120, minwidth=100, anchor='center')

    # Add tags for alternating row colors
    passwordTree.tag_configure('oddrow', background='#E8E8E8')
    passwordTree.tag_configure('evenrow', background='white')

    # Allow sorting by column
    for col in ('website', 'username', 'email'):
        passwordTree.heading(col, text=col.capitalize(), command=lambda _col=col: treeview_sort_column(passwordTree, _col, False))
    
    # Button Frame
    buttonFrame = Frame(rightFrame)
    editButton = Button(buttonFrame, text="Edit", font=("Arial", 10, "bold"), bg="orange", width=8, command=editPassword)
    deleteButton = Button(buttonFrame, text="Delete", font=("Arial", 10, "bold"), bg="lightcoral", width=8, command=deletePassword)
    refreshButton = Button(buttonFrame, text="Refresh", font=("Arial", 10, "bold"), bg="lightgray", width=8, command=updatePasswords)
    
    # =================================================================
    # Context Menu
    # =================================================================
    
    context_menu = Menu(passwordTree, tearoff=0)
    context_menu.add_command(label="Copy Username", command=lambda: copy_from_selection('username'))
    context_menu.add_command(label="Copy Email", command=lambda: copy_from_selection('email'))
    context_menu.add_command(label="Copy Password", command=lambda: copy_from_selection('password'))
    context_menu.add_separator()
    context_menu.add_command(label="View/Edit Details", command=view_details_from_menu)
    context_menu.add_command(label="Delete Entry", command=deletePassword)

    def popup(event):
        iid = passwordTree.identify_row(event.y)
        if iid:
            passwordTree.selection_set(iid)
            passwordTree.focus(iid)
            context_menu.post(event.x_root, event.y_root)

    # =================================================================
    # Pack UI Elements
    # =================================================================

    # Initial Frame (Login or Create) - This will cover the entire window initially
    if not checkIfMasterPasswordIsSet():
        createLabel.pack(pady=5)
        createEntry.pack(pady=5)
        confirmLabel.pack(pady=5)
        confirmEntry.pack(pady=5)
        createButton.pack(pady=5)
        createPasswordFrame.pack(pady=20)
    else:
        loginLabel.pack(pady=5)
        loginEntry.pack(pady=5)
        loginButton.pack(pady=5)
        deleteMasterButton.pack(pady=5)
        loginFrame.pack(pady=20)
    
    # --- Pack Left Frame ---
    siteLabel.pack(pady=2)
    siteEntry.pack(pady=2, fill=X, expand=True)
    usernameLabel.pack(pady=2)
    usernameEntry.pack(pady=2, fill=X, expand=True)
    emailLabel.pack(pady=2)
    emailEntry.pack(pady=2, fill=X, expand=True)
    websiteInfoFrame.pack(pady=5, fill="x")
    
    passwordLabel.pack(pady=2)
    passwordEntry.pack(side=LEFT, fill=X, expand=True)
    copyGenPassButton.pack(side=LEFT, padx=5)
    strengthLabel.pack(pady=(2,10))
    passwordInfoFrame.pack(pady=5, fill="x")
    
    generateButton.pack(side=LEFT, fill=X, expand=True, padx=(0,5))
    advancedButton.pack(side=LEFT, padx=(5,0))
    buttonActionsFrame.pack(pady=5, fill="x")
    addButton.pack(pady=(10,5), fill="x")
    
    # --- Pack Right Frame ---
    listLabel.pack(pady=5)
    searchEntry.pack(side=LEFT, fill="x", expand=True)
    searchFilter.pack(side=LEFT, padx=5)
    searchButton.pack(side=LEFT, padx=5)
    searchFrame.pack(fill="x", pady=5)
    
    # Pack scrollbars and treeview
    v_scrollbar.pack(side=RIGHT, fill=Y)
    h_scrollbar.pack(side='bottom', fill='x')
    passwordTree.pack(side=LEFT, fill=BOTH, expand=True)
    passwordTree.bind("<Double-1>", on_double_click)
    passwordTree.bind("<Button-3>", popup)
    listFrame.pack(fill=BOTH, expand=True, pady=5)
    
    editButton.pack(side=LEFT, padx=5)
    deleteButton.pack(side=LEFT, padx=5)
    refreshButton.pack(side=LEFT, padx=5)
    buttonFrame.pack(pady=5)
    
    leftFrame.pack(side=LEFT, fill=Y, padx=20, pady=20)
    rightFrame.pack(side=RIGHT, fill=BOTH, expand=True, padx=20, pady=20)
    
    # =================================================================
    # Event Bindings
    # =================================================================
    
    loginEntry.bind('<Return>', checkMasterPassword)
    createEntry.bind('<Return>', createNewMasterPassword)
    confirmEntry.bind('<Return>', createNewMasterPassword)
    searchEntry.bind('<KeyRelease>', searchPasswords)
    searchFilter.bind("<<ComboboxSelected>>", searchPasswords)
    
    # Start Application
    mainWindow.mainloop()

# Start the application
startGuiApplication()