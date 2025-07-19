from tkinter import Tk, Frame, Label, Entry, Button, Checkbutton, IntVar, END, Listbox, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH, messagebox, ttk, StringVar, Toplevel, X, Menu, TOP
from encryption import hashText
from fileHandler import savePasswordsToFile, loadPasswordsFromFile
from passwordGenerator import generatePasswordString

class PasswordManager:
    def __init__(self):
        self.window = Tk()
        self.window.title("Paswo - Password Manager")
        self.window.geometry("1400x800")
        
        # Initialize variables
        self.current_master_password = None
        self.is_dark_mode = IntVar(value=1) # 0 for light, 1 for dark
        self.light_theme = {
            "bg": "#F0F0F0", "fg": "#333333", "entry_bg": "white",
            "button_bg": "lightgray", "button_fg": "black", "frame_bg": "#E0E0E0",
            "tree_bg": "white", "tree_fg": "black", "tree_select_bg": "#0078D7",
            "tree_select_fg": "white", "tree_heading_bg": "#DDDDDD", "tree_heading_fg": "black"
        }
        self.dark_theme = {
            "bg": "#2E2E2E", "fg": "#E0E0E0", "entry_bg": "#3E3E3E",
            "button_bg": "#505050", "button_fg": "#E0E0E0", "frame_bg": "#3A3A3A",
            "tree_bg": "#3E3E3E", "tree_fg": "#E0E0E0", "tree_select_bg": "#0056B3",
            "tree_select_fg": "white", "tree_heading_bg": "#4A4A4A", "tree_heading_fg": "#E0E0E0"
        }
        self.current_theme = self.dark_theme

        self.themed_widgets = [] # List to hold widgets for theme application

        self.initialize_variables()
        self.create_frames()
        self.create_login_ui()
        self.create_main_ui()
        self.apply_theme() # apply initial theme
        
        # Show initial screen
        if not self.check_if_master_password_exists():
            self.show_create_password_screen()
        else:
            self.show_login_screen()
    
    def initialize_variables(self):
        # Special character variables
        self.special_chars = {
            'exclamation': IntVar(value=1),
            'dollar': IntVar(value=1),
            'hash': IntVar(value=1),
            'question': IntVar(value=1),
            'at': IntVar(value=1),
            'ampersand': IntVar(value=1),
            'asterisk': IntVar(value=1),
            'caret': IntVar(value=1),
            'euro': IntVar(value=1),
            'percent': IntVar(value=1),
            'plus': IntVar(value=1)
        }
        
        # Other settings
        self.uppercase_var = IntVar(value=1)
        self.dashes_var = IntVar(value=0)
        self.exclude_similar_var = IntVar(value=0)
        self.length_var = StringVar(value="12")
        self.dash_spacing_var = StringVar(value="4")
        
        # Complexity requirements
        self.require_upper_var = IntVar(value=1)
        self.require_digits_var = IntVar(value=1)
        self.require_special_var = IntVar(value=1)
        self.min_upper_var = StringVar(value="2")
        self.min_digits_var = StringVar(value="2")
        self.min_special_var = StringVar(value="2")
        
        # Additional requirements
        self.required_text_var = StringVar(value="")
        self.exclude_chars_var = StringVar(value="")
        
        # Search variables
        self.search_filter_var = StringVar(value="All")
    
    def add_themed_widget(self, widget, widget_type):
        self.themed_widgets.append({"widget": widget, "type": widget_type})

    def create_frames(self):
        # Create main frames
        self.login_frame = Frame(self.window)
        self.add_themed_widget(self.login_frame, "frame")
        self.create_password_frame = Frame(self.window)
        self.add_themed_widget(self.create_password_frame, "frame")
        
        # Create main UI frames
        self.main_frame = Frame(self.window)
        self.add_themed_widget(self.main_frame, "frame")
        self.left_frame = Frame(self.main_frame, width=450, padx=10, pady=10)
        self.add_themed_widget(self.left_frame, "frame")
        self.right_frame = Frame(self.main_frame, padx=10, pady=10)
        self.add_themed_widget(self.right_frame, "frame")
        
        # These frames will be packed when their respective screens are shown, not here.

    def create_login_ui(self):
        # Login screen
        self.login_label = Label(self.login_frame, text="Master password:")
        self.add_themed_widget(self.login_label, "label")
        
        self.login_entry = Entry(self.login_frame, show="*")
        self.add_themed_widget(self.login_entry, "entry")
        
        self.login_button = Button(self.login_frame, text="Login", command=self.check_master_password,
               font=("Arial", 11, "bold"), bg="lightgreen")
        self.add_themed_widget(self.login_button, "button")
        
        self.delete_master_button = Button(self.login_frame, text="Reset All Data", command=self.reset_all_data,
               font=("Arial", 10, "bold"), bg="lightcoral")
        self.add_themed_widget(self.delete_master_button, "button")
        
        # Create password screen
        self.create_label = Label(self.create_password_frame, text="Create new master password:")
        self.add_themed_widget(self.create_label, "label")
        
        self.create_entry = Entry(self.create_password_frame, show="*")
        self.add_themed_widget(self.create_entry, "entry")
        
        self.confirm_label = Label(self.create_password_frame, text="Confirm master password:")
        self.add_themed_widget(self.confirm_label, "label")
        
        self.confirm_entry = Entry(self.create_password_frame, show="*")
        self.add_themed_widget(self.confirm_entry, "entry")
        
        self.hint_label = Label(self.create_password_frame, text="Password hint (required):")
        self.add_themed_widget(self.hint_label, "label")
        
        self.hint_entry = Entry(self.create_password_frame)
        self.add_themed_widget(self.hint_entry, "entry")
        
        self.create_button = Button(self.create_password_frame, text="Create", command=self.create_master_password,
               font=("Arial", 11, "bold"), bg="lightblue")
        self.add_themed_widget(self.create_button, "button")
    
    def create_main_ui(self):
        # Dark mode toggle (this is directly on self.window)
        self.dark_mode_frame_instance = Frame(self.window)
        self.add_themed_widget(self.dark_mode_frame_instance, "frame")
        dark_mode_check = Checkbutton(self.dark_mode_frame_instance, text="Dark Mode", variable=self.is_dark_mode, command=self.toggle_dark_mode)
        self.add_themed_widget(dark_mode_check, "checkbutton")
        
        # Left side - Website info
        self.website_frame = Frame(self.left_frame, relief="solid", bd=1, padx=10, pady=10)
        self.add_themed_widget(self.website_frame, "frame")
        
        self.website_info_label = Label(self.website_frame, text="Website Information", font=("Arial", 12, "bold"))
        self.add_themed_widget(self.website_info_label, "label")
        
        self.website_name_label = Label(self.website_frame, text="Website name:")
        self.add_themed_widget(self.website_name_label, "label")
        self.website_entry = Entry(self.website_frame, width=30)
        self.add_themed_widget(self.website_entry, "entry")
        
        self.username_label = Label(self.website_frame, text="Username:")
        self.add_themed_widget(self.username_label, "label")
        self.username_entry = Entry(self.website_frame, width=30)
        self.add_themed_widget(self.username_entry, "entry")
        
        self.email_label = Label(self.website_frame, text="Email:")
        self.add_themed_widget(self.email_label, "label")
        self.email_entry = Entry(self.website_frame, width=30)
        self.add_themed_widget(self.email_entry, "entry")
        
        # Password section
        self.password_frame = Frame(self.left_frame, relief="solid", bd=1, padx=10, pady=10)
        self.add_themed_widget(self.password_frame, "frame")
        
        self.generated_password_label = Label(self.password_frame, text="Generated Password", font=("Arial", 12, "bold"))
        self.add_themed_widget(self.generated_password_label, "label")
        self.password_label = Label(self.password_frame, text="Password:")
        self.add_themed_widget(self.password_label, "label")
        self.password_entry = Entry(self.password_frame, width=30)
        self.add_themed_widget(self.password_entry, "entry")
        
        # Password generation controls
        self.controls_frame = Frame(self.password_frame)
        self.add_themed_widget(self.controls_frame, "frame")
        
        self.generate_button = Button(self.controls_frame, text="Generate", command=self.generate_password,
               font=("Arial", 11, "bold"), bg="lightblue")
        self.add_themed_widget(self.generate_button, "button")
        
        # Advanced options button and frame
        self.advanced_button = Button(self.controls_frame, text="Advanced...", command=self.toggle_advanced_options)
        self.add_themed_widget(self.advanced_button, "button")
        
        # Advanced options frame
        self.advanced_frame = Frame(self.left_frame, relief="solid", bd=1, padx=10, pady=10)
        self.add_themed_widget(self.advanced_frame, "frame")
        
        # Special Characters Section
        self.special_chars_frame = Frame(self.advanced_frame)
        self.add_themed_widget(self.special_chars_frame, "frame")
        
        self.special_header_frame = Frame(self.special_chars_frame)
        self.add_themed_widget(self.special_header_frame, "frame")
        self.special_chars_label = Label(self.special_header_frame, text="Special chars:", font=("Arial", 10, "bold"))
        self.add_themed_widget(self.special_chars_label, "label")
        self.toggle_all_button = Button(self.special_header_frame, text="Toggle All", command=self.toggle_all_special)
        self.add_themed_widget(self.toggle_all_button, "button")
        
        special_chars_data = [
            ("!", 'exclamation'), ("$", 'dollar'), ("#", 'hash'), ("?", 'question'),
            ("@", 'at'), ("&", 'ampersand'), ("*", 'asterisk'), ("^", 'caret'),
            ("€", 'euro'), ("%", 'percent'), ("+", 'plus')
        ]
        
        self.special_char_rows = []
        for i in range(0, len(special_chars_data), 5):
            row = Frame(self.special_chars_frame)
            self.add_themed_widget(row, "frame")
            self.special_char_rows.append(row)
            for char, var_name in special_chars_data[i:i+5]:
                checkbutton = Checkbutton(row, text=char, variable=self.special_chars[var_name])
                self.add_themed_widget(checkbutton, "checkbutton")
        
        # Complexity Requirements
        self.complexity_frame = Frame(self.advanced_frame)
        self.add_themed_widget(self.complexity_frame, "frame")
        self.complexity_rules_label = Label(self.complexity_frame, text="Complexity Rules:", font=("Arial", 10, "bold"))
        self.add_themed_widget(self.complexity_rules_label, "label")
        
        # Length and spacing
        self.length_frame = Frame(self.complexity_frame)
        self.add_themed_widget(self.length_frame, "frame")
        self.length_label = Label(self.length_frame, text="Length:")
        self.add_themed_widget(self.length_label, "label")
        self.length_entry = Entry(self.length_frame, textvariable=self.length_var, width=4)
        self.add_themed_widget(self.length_entry, "entry")
        
        # Dashes
        self.dash_frame = Frame(self.complexity_frame)
        self.add_themed_widget(self.dash_frame, "frame")
        self.add_dashes_check = Checkbutton(self.dash_frame, text="Add dashes every", variable=self.dashes_var)
        self.add_themed_widget(self.add_dashes_check, "checkbutton")
        self.dash_spacing_entry = Entry(self.dash_frame, textvariable=self.dash_spacing_var, width=2)
        self.add_themed_widget(self.dash_spacing_entry, "entry")
        self.chars_label = Label(self.dash_frame, text="chars")
        self.add_themed_widget(self.chars_label, "label")
        
        # Upper/digits/special requirements
        self.complexity_rows = []
        for (text, req_var, min_var) in [
            ("uppercase", self.require_upper_var, self.min_upper_var),
            ("digits", self.require_digits_var, self.min_digits_var),
            ("special chars", self.require_special_var, self.min_special_var)
        ]:
            frame = Frame(self.complexity_frame)
            self.add_themed_widget(frame, "frame")
            self.complexity_rows.append(frame)
            require_check = Checkbutton(frame, text="Require", variable=req_var)
            self.add_themed_widget(require_check, "checkbutton")
            min_entry = Entry(frame, textvariable=min_var, width=2)
            self.add_themed_widget(min_entry, "entry")
            or_more_label = Label(frame, text=f"or more {text}")
            self.add_themed_widget(or_more_label, "label")
        
        # Other options
        self.other_options_frame = Frame(self.advanced_frame)
        self.add_themed_widget(self.other_options_frame, "frame")
        self.uppercase_check = Checkbutton(self.other_options_frame, text="Uppercase", variable=self.uppercase_var)
        self.add_themed_widget(self.uppercase_check, "checkbutton")
        self.exclude_similar_check = Checkbutton(self.other_options_frame, text="Exclude similar chars (I,l,1,O,0)", 
                   variable=self.exclude_similar_var)
        self.add_themed_widget(self.exclude_similar_check, "checkbutton")
        
        # Required/Excluded text
        self.required_text_frame = Frame(self.advanced_frame)
        self.add_themed_widget(self.required_text_frame, "frame")
        self.required_text_label = Label(self.required_text_frame, text="Required text:")
        self.add_themed_widget(self.required_text_label, "label")
        self.required_text_entry = Entry(self.required_text_frame, textvariable=self.required_text_var)
        self.add_themed_widget(self.required_text_entry, "entry")
        
        self.exclude_chars_frame = Frame(self.advanced_frame)
        self.add_themed_widget(self.exclude_chars_frame, "frame")
        self.exclude_chars_label = Label(self.exclude_chars_frame, text="Exclude chars:")
        self.add_themed_widget(self.exclude_chars_label, "label")
        self.exclude_chars_entry = Entry(self.exclude_chars_frame, textvariable=self.exclude_chars_var)
        self.add_themed_widget(self.exclude_chars_entry, "entry")
        
        # Add button
        self.add_entry_button = Button(self.left_frame, text="Add Entry", command=self.add_password,
               font=("Arial", 11, "bold"), bg="lightgreen")
        self.add_themed_widget(self.add_entry_button, "button")
        
        # Right side - Password list
        self.saved_passwords_label = Label(self.right_frame, text="Saved Passwords:", font=("Arial", 12, "bold"))
        self.add_themed_widget(self.saved_passwords_label, "label")
        
        # Search
        self.search_frame = Frame(self.right_frame)
        self.add_themed_widget(self.search_frame, "frame")
        self.search_label = Label(self.search_frame, text="Search:")
        self.add_themed_widget(self.search_label, "label")
        self.search_entry = Entry(self.search_frame)
        self.add_themed_widget(self.search_entry, "entry")
        self.search_filter_combo = ttk.Combobox(self.search_frame, textvariable=self.search_filter_var,
                    values=["All", "Website", "Username", "Email"],
                    state="readonly", width=10)
        self.add_themed_widget(self.search_filter_combo, "ttk_widget")
        self.search_button = Button(self.search_frame, text="Search", command=self.search_passwords)
        self.add_themed_widget(self.search_button, "button")
        
        # Password list
        self.list_frame = Frame(self.right_frame)
        self.add_themed_widget(self.list_frame, "frame")
        
        self.password_tree = ttk.Treeview(self.list_frame,
                                        columns=('website', 'username', 'email', 'password', 'copy_user', 'copy_email', 'copy_pass', 'copy_website_col', 'edit_user', 'edit_email', 'edit_pass', 'edit_website'),
                                        show='headings')
        self.add_themed_widget(self.password_tree, "ttk_widget")
        
        # Scrollbars
        self.vsb = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.password_tree.yview)
        self.add_themed_widget(self.vsb, "ttk_widget")
        self.hsb = ttk.Scrollbar(self.list_frame, orient="horizontal", command=self.password_tree.xview)
        self.add_themed_widget(self.hsb, "ttk_widget")
        self.password_tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        
        # Configure columns
        self.password_tree.heading('website', text='Website', command=lambda: self.sort_treeview('website'))
        self.password_tree.heading('username', text='Username', command=lambda: self.sort_treeview('username'))
        self.password_tree.heading('email', text='Email', command=lambda: self.sort_treeview('email'))
        self.password_tree.heading('password', text='Password')
        self.password_tree.heading('copy_user', text='')
        self.password_tree.heading('copy_email', text='')
        self.password_tree.heading('copy_pass', text='')
        self.password_tree.heading('copy_website_col', text='') # new copy website column
        self.password_tree.heading('edit_user', text='') # new column
        self.password_tree.heading('edit_email', text='') # new column
        self.password_tree.heading('edit_pass', text='') # new column
        self.password_tree.heading('edit_website', text='') # new column
        
        self.password_tree.column('website', width=200, minwidth=150)
        self.password_tree.column('username', width=150, minwidth=100)
        self.password_tree.column('email', width=200, minwidth=150)
        self.password_tree.column('password', width=100, minwidth=80)
        self.password_tree.column('copy_user', width=30, minwidth=30, anchor='center')
        self.password_tree.column('copy_email', width=30, minwidth=30, anchor='center')
        self.password_tree.column('copy_pass', width=30, minwidth=30, anchor='center')
        self.password_tree.column('copy_website_col', width=30, minwidth=30, anchor='center') # new copy website column
        self.password_tree.column('edit_user', width=30, minwidth=30, anchor='center') # new column
        self.password_tree.column('edit_email', width=30, minwidth=30, anchor='center') # new column
        self.password_tree.column('edit_pass', width=30, minwidth=30, anchor='center') # new column
        self.password_tree.column('edit_website', width=30, minwidth=30, anchor='center') # new column
        
        # Buttons
        self.button_frame = Frame(self.right_frame)
        self.add_themed_widget(self.button_frame, "frame")
        self.delete_button = Button(self.button_frame, text="Delete", command=self.delete_password,
               font=("Arial", 10, "bold"), bg="lightcoral")
        self.add_themed_widget(self.delete_button, "button")
        self.refresh_button = Button(self.button_frame, text="Refresh", command=self.refresh_passwords,
               font=("Arial", 10, "bold"), bg="lightgray")
        self.add_themed_widget(self.refresh_button, "button")
        
        # Context menu
        self.context_menu = Menu(self.password_tree, tearoff=0)
        self.context_menu.add_command(label="Copy Username", command=lambda: self.copy_value('username'))
        self.context_menu.add_command(label="Copy Email", command=lambda: self.copy_value('email'))
        self.context_menu.add_command(label="Copy Password", command=lambda: self.copy_value('password'))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Entry", command=self.delete_password)
        
        # Bind right-click menu
        self.password_tree.bind("<Button-3>", self.show_context_menu)
        
        # Bind click events for copy buttons
        self.password_tree.bind("<Button-1>", self.handle_click)

    def _pack_main_ui_elements(self):
        # Pack dark mode toggle (top-level, always visible with main UI)
        self.dark_mode_frame_instance.pack(side=TOP, anchor="ne", padx=10, pady=5)
        self.dark_mode_frame_instance.winfo_children()[0].pack(side=RIGHT) # Pack the checkbutton

        # Pack main frames
        self.main_frame.pack(fill=BOTH, expand=True)
        self.left_frame.pack(side=LEFT, fill=Y)
        self.right_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Explicitly pack the major sections of the left frame
        self.website_frame.pack(fill=X, pady=(0, 10))
        # Pack children of website_frame
        self.website_info_label.pack(pady=(0, 5))
        self.website_name_label.pack(anchor="w")
        self.website_entry.pack(fill=X)
        self.username_label.pack(anchor="w")
        self.username_entry.pack(fill=X)
        self.email_label.pack(anchor="w")
        self.email_entry.pack(fill=X)

        self.password_frame.pack(fill=X, pady=10)
        # Pack children of password_frame
        self.generated_password_label.pack(pady=(0, 5))
        self.password_label.pack(anchor="w")
        self.password_entry.pack(fill=X)

        self.controls_frame.pack(fill=X, pady=5) # pack controls frame within password_frame
        # Pack children of controls_frame
        self.generate_button.pack(side=LEFT, padx=5)
        self.advanced_button.pack(side=LEFT)

        self.add_entry_button.pack(fill=X, pady=10) # always visible

        # Pack advanced options frame if it was previously visible
        if self.advanced_button.cget("text") == "Hide Advanced":
            self.advanced_frame.pack(pady=10, fill="x")
            # Pack advanced options sub-elements only if advanced_frame is packed
            self.special_chars_frame.pack(fill=X, pady=5)
            self.special_header_frame.pack(fill=X)
            self.special_chars_label.pack(side=LEFT)
            self.toggle_all_button.pack(side=LEFT, padx=5)
            for row in self.special_char_rows:
                row.pack(fill=X)
                for checkbutton in row.winfo_children(): checkbutton.pack(side=LEFT)

            self.complexity_frame.pack(fill=X, pady=5)
            self.complexity_rules_label.pack(anchor="w")

            self.length_frame.pack(fill=X)
            self.length_label.pack(side=LEFT)
            self.length_entry.pack(side=LEFT, padx=2)

            self.dash_frame.pack(fill=X)
            self.add_dashes_check.pack(side=LEFT)
            self.dash_spacing_entry.pack(side=LEFT, padx=2)
            self.chars_label.pack(side=LEFT)

            for row in self.complexity_rows:
                row.pack(fill=X)
                for widget in row.winfo_children(): widget.pack(side=LEFT)

            self.other_options_frame.pack(fill=X, pady=5)
            self.uppercase_check.pack(side=LEFT, padx=5)
            self.exclude_similar_check.pack(side=LEFT)

            self.required_text_frame.pack(fill=X, pady=5)
            self.required_text_label.pack(side=LEFT)
            self.required_text_entry.pack(side=LEFT, fill=X, expand=True)

            self.exclude_chars_frame.pack(fill=X, pady=5)
            self.exclude_chars_label.pack(side=LEFT)
            self.exclude_chars_entry.pack(side=LEFT, fill=X, expand=True)

        # Explicitly pack the major sections of the right frame
        self.saved_passwords_label.pack(anchor="w", pady=(0, 10))
        self.search_frame.pack(fill=X, pady=(0, 10))
        # Pack children of search_frame
        self.search_label.pack(side=LEFT)
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.search_filter_combo.pack(side=LEFT)
        self.search_button.pack(side=LEFT, padx=5)

        self.list_frame.pack(fill=BOTH, expand=True)
        # Pack children of list_frame
        self.password_tree.grid(row=0, column=0, sticky='nsew')
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.hsb.grid(row=1, column=0, sticky='ew')
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(0, weight=1)

        self.button_frame.pack(fill=X, pady=10)
        # Pack children of button_frame
        self.delete_button.pack(side=LEFT, padx=5)
        self.refresh_button.pack(side=LEFT, padx=5)

    def _forget_main_ui_elements(self):
        # Unpack dark mode toggle (top-level)
        self.dark_mode_frame_instance.pack_forget()
        self.dark_mode_frame_instance.winfo_children()[0].pack_forget() # Unpack the checkbutton

        # Unpack main frames
        self.main_frame.pack_forget()
        self.left_frame.pack_forget()
        self.right_frame.pack_forget()
        
        # Unpack all widgets from left_frame
        self.website_frame.pack_forget()
        self.website_info_label.pack_forget()
        self.website_name_label.pack_forget()
        self.website_entry.pack_forget()
        self.username_label.pack_forget()
        self.username_entry.pack_forget()
        self.email_label.pack_forget()
        self.email_entry.pack_forget()
        
        self.password_frame.pack_forget()
        self.generated_password_label.pack_forget()
        self.password_label.pack_forget()
        self.password_entry.pack_forget()
        
        self.controls_frame.pack_forget()
        self.generate_button.pack_forget()
        self.advanced_button.pack_forget()

        self.advanced_frame.pack_forget()
        # self.add_entry_button.pack_forget() # removed, should always be visible

        # Unpack all widgets from right_frame
        self.saved_passwords_label.pack_forget()
        self.search_frame.pack_forget()
        self.search_label.pack_forget()
        self.search_entry.pack_forget()
        self.search_filter_combo.pack_forget()
        self.search_button.pack_forget()
        self.list_frame.pack_forget()
        self.password_tree.grid_forget()
        self.vsb.grid_forget()
        self.hsb.grid_forget()
        self.button_frame.pack_forget()
        self.delete_button.pack_forget()
        self.refresh_button.pack_forget()
    
    def show_login_screen(self):
        self._forget_main_ui_elements()
        self.create_password_frame.pack_forget()
        
        self.login_frame.pack(pady=20)
        self.login_label.pack(pady=5)
        self.login_entry.pack(pady=5)
        self.login_button.pack(pady=5)
        self.delete_master_button.pack(pady=5)
        self.login_entry.delete(0, END)
        self.login_entry.focus()
    
    def show_create_password_screen(self):
        self._forget_main_ui_elements()
        self.login_frame.pack_forget()
        
        self.create_password_frame.pack(pady=20)
        self.create_label.pack(pady=5)
        self.create_entry.pack(pady=5)
        self.confirm_label.pack(pady=5)
        self.confirm_entry.pack(pady=5)
        self.hint_label.pack(pady=5)
        self.hint_entry.pack(pady=5)
        self.create_button.pack(pady=5)
        self.create_entry.focus()
    
    def show_main_screen(self):
        self.login_frame.pack_forget()
        self.create_password_frame.pack_forget()
        
        self._pack_main_ui_elements()
        self.refresh_passwords()
        
        # set focus to the first entry widget in the main ui
        self.website_entry.focus_set()
    
    def check_if_master_password_exists(self):
        try:
            with open('master_password.json', 'r') as f:
                content = f.read().strip()
                return content != "" and content != "{}" and '"master_password_hash": ""' not in content
        except:
            return False
    
    def check_master_password(self):
        password = self.login_entry.get()
        stored_hash, hint = self.load_master_password()
        
        if hashText(password) == stored_hash:
            self.current_master_password = password
            self.show_main_screen()
        else:
            if hint:
                pass # messagebox.showinfo("Password Hint", f"Hint: {hint}") # removed
    
    def create_master_password(self):
        password = self.create_entry.get()
        confirm = self.confirm_entry.get()
        hint = self.hint_entry.get()
        
        if not password or not confirm:
            return
        
        if not hint:
            return
        
        if password != confirm:
            return
        
        self.save_master_password(password, hint)
        self.show_login_screen()
    
    def load_master_password(self):
        try:
            with open('master_password.json', 'r') as f:
                import json
                data = json.load(f)
                return data.get("master_password_hash"), data.get("hint")
        except:
            return None, None
    
    def save_master_password(self, password, hint):
        hashed = hashText(password)
        with open('master_password.json', 'w') as f:
            import json
            json.dump({"master_password_hash": hashed, "hint": hint}, f, indent=2)
    
    def reset_all_data(self):
        if messagebox.askyesno("Confirm Reset", "This will delete all saved passwords and reset the master password. Are you sure?"):
            try:
                with open('master_password.json', 'w') as f:
                    f.write('{"master_password_hash": ""}')
                with open('passwords.json', 'w') as f:
                    f.write('{}')
                self.show_create_password_screen()
            except:
                pass
    
    def generate_password(self):
        try:
            length = int(self.length_var.get())
            # if length < 8:
            #     messagebox.showwarning("Warning", "Password length should be at least 8 characters")
            #     return
            
            special_chars = ""
            for char, var in self.special_chars.items():
                if var.get():
                    special_chars += {"exclamation": "!", "dollar": "$", "hash": "#",
                                    "question": "?", "at": "@", "ampersand": "&",
                                    "asterisk": "*", "caret": "^", "euro": "€",
                                    "percent": "%", "plus": "+"}[char]
            
            # Get complexity requirements
            min_upper = int(self.min_upper_var.get()) if self.require_upper_var.get() else 0
            min_digits = int(self.min_digits_var.get()) if self.require_digits_var.get() else 0
            min_special = int(self.min_special_var.get()) if self.require_special_var.get() else 0
            
            password = generatePasswordString(
                length=length,
                useUppercase=bool(self.uppercase_var.get()),
                minUppercase=min_upper,
                minDigits=min_digits,
                minSpecial=min_special,
                specialChars=special_chars,
                useDashes=bool(self.dashes_var.get()),
                dashSpacing=int(self.dash_spacing_var.get()) if self.dashes_var.get() else 0,
                exclude_similar=bool(self.exclude_similar_var.get()),
                requiredText=self.required_text_var.get(),
                exclude_chars=self.exclude_chars_var.get()
            )
            
            if password:
                self.password_entry.delete(0, END)
                self.password_entry.insert(0, password)
        except ValueError:
            pass
    
    def add_password(self):
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        try:
            passwords = loadPasswordsFromFile(self.current_master_password)
            passwords[website] = {
                'username': username,
                'email': email,
                'password': password
            }
            
            if savePasswordsToFile(passwords, self.current_master_password):
                self.refresh_passwords()
                self.website_entry.delete(0, END)
                self.username_entry.delete(0, END)
                self.email_entry.delete(0, END)
                self.password_entry.delete(0, END)
            else:
                pass
        except Exception as e:
            pass
    
    def sort_treeview(self, col):
        items = [(self.password_tree.set(item, col), item) for item in self.password_tree.get_children('')]
        items.sort()
        for index, (val, item) in enumerate(items):
            self.password_tree.move(item, '', index)
    
    def show_context_menu(self, event):
        item = self.password_tree.identify_row(event.y)
        self.password_tree.selection_set(item)
        self.context_menu.post(event.x_root, event.y_root)
    
    def handle_click(self, event):
        region = self.password_tree.identify_region(event.x, event.y)
        if region == "cell":
            column_id = self.password_tree.identify_column(event.x)
            item_id = self.password_tree.identify_row(event.y)
            if column_id == '#5': # copy username column
                self.copy_value('username', item_id)
            elif column_id == '#6': # copy email column
                self.copy_value('email', item_id)
            elif column_id == '#7': # copy password column
                self.copy_value('password', item_id)
            elif column_id == '#8': # copy website column (new dedicated column)
                self.copy_value('website', item_id)
            elif column_id == '#9': # edit username column
                self.start_inline_edit(item_id, 'username')
            elif column_id == '#10': # edit email column
                self.start_inline_edit(item_id, 'email')
            elif column_id == '#11': # edit password column
                self.start_inline_edit(item_id, 'password')
            elif column_id == '#12': # edit website column
                self.start_inline_edit(item_id, 'website')

    def start_inline_edit(self, item_id, field_type):
        # get current values for the row
        current_values = self.password_tree.item(item_id, 'values')
        website = current_values[0]
        
        # get the actual, unmasked password data
        passwords = loadPasswordsFromFile(self.current_master_password)
        details = passwords.get(website, {})

        # determine which index and actual value to use for editing
        col_index_map = {'username': 1, 'email': 2, 'password': 3, 'website': 0}
        treeview_col_index = col_index_map.get(field_type)

        if treeview_col_index is None:
            print(f"error: invalid field_type for inline edit: {field_type}")
            return

        # get the actual value for editing (unmasked for password)
        current_value_for_edit = website_name = current_values[0]
        if field_type == 'password':
            current_value_for_edit = details.get(field_type, '')
        elif field_type == 'username':
            current_value_for_edit = details.get('username', '')
        elif field_type == 'email':
            current_value_for_edit = details.get('email', '')
        elif field_type == 'website':
            current_value_for_edit = website_name # website name is the key

        # get column bounding box
        x, y, width, height = self.password_tree.bbox(item_id, column=f'#{treeview_col_index + 1}')

        # create an entry widget
        edit_entry = Entry(self.password_tree, 
                           bg=self.current_theme["entry_bg"], 
                           fg=self.current_theme["fg"], 
                           insertbackground=self.current_theme["fg"])
        edit_entry.place(x=x, y=y, width=width, height=height)
        edit_entry.insert(0, current_value_for_edit)
        edit_entry.focus_set()

        def save_inline_edit(event=None):
            new_value = edit_entry.get()
            
            # update the underlying data
            passwords = loadPasswordsFromFile(self.current_master_password) # reload to get latest
            
            # handle website name change (which is the key)
            if field_type == 'website':
                if new_value != website: # if website name has changed
                    # check if new website name already exists
                    if new_value in passwords:
                        print(f"error: website '{new_value}' already exists")
                        edit_entry.destroy()
                        return
                    
                    # create a new entry with the new website name
                    passwords[new_value] = passwords[website]
                    del passwords[website] # delete old entry
                    website = new_value # update website to new value for subsequent operations
            
            if website in passwords:
                # ensure the entry is a dictionary
                if not isinstance(passwords[website], dict):
                    # convert old string format to dict if necessary
                    passwords[website] = {
                        'username': '',
                        'email': '',
                        'password': passwords[website] # put old string into password field
                    }

                # update the specific field if it's not the website (which was handled above)
                if field_type != 'website':
                    passwords[website][field_type] = new_value

                if savePasswordsToFile(passwords, self.current_master_password):
                    self.refresh_passwords()
            edit_entry.destroy() # remove the entry widget

        edit_entry.bind("<Return>", save_inline_edit)
        edit_entry.bind("<FocusOut>", save_inline_edit)
    
    def copy_value(self, field_type, item=None):
        if item is None:
            item = self.password_tree.selection()[0]
        
        values = self.password_tree.item(item)['values']
        
        try:
            if field_type == 'password':
                # Get actual password from stored data
                website = values[0]
                passwords = loadPasswordsFromFile(self.current_master_password)
                if website in passwords:
                    value = passwords[website]['password']
                else:
                    return
            else:
                # Get displayed value
                idx = {'username': 1, 'email': 2, 'website': 0}.get(field_type, None)
                if idx is None:
                    # Fallback for unexpected field_type
                    return
                value = values[idx]
            
            # Copy to clipboard
            self.window.clipboard_clear()
            self.window.clipboard_append(value)
            
            # Update copy button icon temporarily
            col_idx = {'username': 4, 'email': 5, 'password': 6, 'website': 0}.get(field_type)
            current_values = list(values)
            current_values[col_idx] = '✓'
            self.password_tree.item(item, values=tuple(current_values))
            
            # Reset icon after 2 seconds
            self.window.after(2000, lambda: self.reset_copy_icon(item, field_type))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy {field_type}: {str(e)}")
    
    def reset_copy_icon(self, item, field_type):
        try:
            values = list(self.password_tree.item(item)['values'])
            col_idx = {'username': 4, 'email': 5, 'password': 6, 'website': 0}.get(field_type)
            values[col_idx] = '📋'
            self.password_tree.item(item, values=tuple(values))
        except:
            pass
    
    def refresh_passwords(self):
        for item in self.password_tree.get_children():
            self.password_tree.delete(item)
        
        try:
            passwords = loadPasswordsFromFile(self.current_master_password)
            for website, details in passwords.items():
                username = ''
                email = ''
                password_display = '••••••••' # default masked password
                actual_password = ''

                if isinstance(details, dict):
                    username = details.get('username', '')
                    email = details.get('email', '')
                    actual_password = details.get('password', '')
                else:
                    # if 'details' is a string, assume it's an old plain password or malformed entry
                    actual_password = details
                    password_display = details # display the string itself for debugging malformed entries

                self.password_tree.insert('', 'end', values=(
                    website,
                    username,
                    email,
                    password_display,
                    '📋',  # Copy username button
                    '📋',  # Copy email button
                    '📋',   # Copy password button
                    '📋',   # Copy website button
                    '✎',  # Edit username button
                    '✎',  # Edit email button
                    '✎',   # Edit password button
                    '✎'   # Edit website button
                ))
        except Exception as e:
            pass
    
    def search_passwords(self):
        query = self.search_entry.get().lower()
        filter_type = self.search_filter_var.get()
        
        for item in self.password_tree.get_children():
            self.password_tree.delete(item)
        
        try:
            passwords = loadPasswordsFromFile(self.current_master_password)
            for website, details in passwords.items():
                matches = False
                if filter_type == "All":
                    matches = (query in website.lower() or
                             query in details.get('username', '').lower() or
                             query in details.get('email', '').lower())
                elif filter_type == "Website":
                    matches = query in website.lower()
                elif filter_type == "Username":
                    matches = query in details.get('username', '').lower()
                elif filter_type == "Email":
                    matches = query in details.get('email', '').lower()
                
                if matches:
                    self.password_tree.insert('', 'end', values=(
                        website,
                        details.get('username', ''),
                        details.get('email', ''),
                        '••••••••'
                    ))
        except Exception as e:
            # messagebox.showerror("Error", f"Failed to search passwords: {str(e)}") # removed
            pass
    
    def delete_password(self):
        item = self.password_tree.item(self.password_tree.selection()[0])
        website = item['values'][0]
        
        # if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the entry for {website}?"): # removed
        try:
            passwords = loadPasswordsFromFile(self.current_master_password)
            if website in passwords:
                del passwords[website]
                if savePasswordsToFile(passwords, self.current_master_password):
                    self.refresh_passwords()
                    # messagebox.showinfo("Success", "Entry deleted successfully") # removed
                else:
                    # messagebox.showerror("Error", "Failed to delete entry") # removed
                    pass
        except Exception as e:
            # messagebox.showerror("Error", f"Failed to delete password: {str(e)}") # removed
            pass
    
    def toggle_all_special(self):
        # Use first checkbox as reference
        new_state = not bool(self.special_chars['exclamation'].get())
        for var in self.special_chars.values():
            var.set(new_state)

    def toggle_advanced_options(self):
        if self.advanced_frame.winfo_ismapped():
            self.advanced_frame.pack_forget()
            # unpack all sub-elements of advanced_frame
            self.special_chars_frame.pack_forget()
            self.special_header_frame.pack_forget()
            self.special_chars_label.pack_forget()
            self.toggle_all_button.pack_forget()
            for row in self.special_char_rows:
                row.pack_forget()
                for checkbutton in row.winfo_children():
                    checkbutton.pack_forget()
            self.complexity_frame.pack_forget()
            self.complexity_rules_label.pack_forget()
            self.length_frame.pack_forget()
            self.length_label.pack_forget()
            self.length_entry.pack_forget()
            self.dash_frame.pack_forget()
            self.add_dashes_check.pack_forget()
            self.dash_spacing_entry.pack_forget()
            self.chars_label.pack_forget()
            for row in self.complexity_rows:
                row.pack_forget()
                for widget in row.winfo_children():
                    widget.pack_forget()
            self.other_options_frame.pack_forget()
            self.uppercase_check.pack_forget()
            self.exclude_similar_check.pack_forget()
            self.required_text_frame.pack_forget()
            self.required_text_label.pack_forget()
            self.required_text_entry.pack_forget()
            self.exclude_chars_frame.pack_forget()
            self.exclude_chars_label.pack_forget()
            self.exclude_chars_entry.pack_forget()

            self.advanced_button.config(text="Advanced...")
        else:
            self.advanced_frame.pack(after=self.add_entry_button, pady=10, fill="x") # pack relative to add_entry_button
            # pack all sub-elements of advanced_frame
            self.special_chars_frame.pack(fill=X, pady=5)
            self.special_header_frame.pack(fill=X)
            self.special_chars_label.pack(side=LEFT)
            self.toggle_all_button.pack(side=LEFT, padx=5)
            for row in self.special_char_rows:
                row.pack(fill=X)
                for checkbutton in row.winfo_children():
                    checkbutton.pack(side=LEFT)
            self.complexity_frame.pack(fill=X, pady=5)
            self.complexity_rules_label.pack(anchor="w")
            self.length_frame.pack(fill=X)
            self.length_label.pack(side=LEFT)
            self.length_entry.pack(side=LEFT, padx=2)
            self.dash_frame.pack(fill=X)
            self.add_dashes_check.pack(side=LEFT)
            self.dash_spacing_entry.pack(side=LEFT, padx=2)
            self.chars_label.pack(side=LEFT)
            for row in self.complexity_rows:
                row.pack(fill=X)
                for widget in row.winfo_children():
                    widget.pack(side=LEFT)
            self.other_options_frame.pack(fill=X, pady=5)
            self.uppercase_check.pack(side=LEFT, padx=5)
            self.exclude_similar_check.pack(side=LEFT)
            self.required_text_frame.pack(fill=X, pady=5)
            self.required_text_label.pack(side=LEFT)
            self.required_text_entry.pack(side=LEFT, fill=X, expand=True)
            self.exclude_chars_frame.pack(fill=X, pady=5)
            self.exclude_chars_label.pack(side=LEFT)
            self.exclude_chars_entry.pack(side=LEFT, fill=X, expand=True)

            self.advanced_button.config(text="Hide Advanced")
    
    def apply_theme(self):
        theme = self.current_theme
        
        # Apply to main window
        self.window.config(bg=theme["bg"])
        
        # Apply to all tracked widgets
        for item in self.themed_widgets:
            widget = item["widget"]
            widget_type = item["type"]

            if widget_type == "frame":
                widget.config(bg=theme["bg"])
            elif widget_type == "label":
                widget.config(bg=theme["bg"], fg=theme["fg"])
            elif widget_type == "entry":
                widget.config(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])
                widget.bind("<Button-1>", lambda event, w=widget: w.focus_set()) # bind click to focus
            elif widget_type == "button":
                widget.config(bg=theme["button_bg"], fg=theme["button_fg"])
            elif widget_type == "checkbutton":
                widget.config(bg=theme["bg"], fg=theme["fg"], selectcolor=theme["entry_bg"])
        
        # Treeview styling
        style = ttk.Style()
        style.theme_use("default") # Reset to default to ensure changes apply
        style.configure("Treeview",
                        background=theme["tree_bg"],
                        foreground=theme["tree_fg"],
                        fieldbackground=theme["tree_bg"],
                        rowheight=25 # Maintain a reasonable row height
                       )
        style.map("Treeview",
                  background=[('selected', theme["tree_select_bg"])],
                  foreground=[('selected', theme["tree_select_fg"])])
        style.configure("Treeview.Heading",
                        background=theme["tree_heading_bg"],
                        foreground=theme["tree_heading_fg"],
                        font=('Arial', 10, 'bold') # Keep font consistent
                       )
        
        # Apply alternating row colors
        self.password_tree.tag_configure('oddrow', background=theme["tree_bg"])
        self.password_tree.tag_configure('evenrow', background=theme["frame_bg"])
    
    def toggle_dark_mode(self):
        if self.is_dark_mode.get() == 1:
            self.current_theme = self.dark_theme
        else:
            self.current_theme = self.light_theme
        self.apply_theme()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PasswordManager()
    app.run()