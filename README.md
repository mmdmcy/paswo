# Local Password Manager

A secure, offline password manager built in Python with Tkinter GUI. This application stores encrypted passwords locally on your computer without requiring internet connectivity or external databases, ensuring maximum privacy and security.

## Author
**mmdmcy** - Solo developer

## Features

### Core Functionality
- **Offline Operation**: Works entirely offline for maximum privacy
- **Master Password Protection**: Secure your password vault with a master password using SHA-256 hashing
- **Custom Encryption**: Implements a custom encryption algorithm inspired by AES principles
- **Local Storage**: All data stored locally in encrypted JSON files
- **User-Friendly Interface**: Clean, intuitive GUI built with Tkinter

### Password Management
- **Store Website Credentials**: Save website name, username, email, and password
- **Edit Existing Entries**: Modify stored credentials easily
- **Delete Entries**: Remove unwanted password entries
- **Clear Display**: Well-organized list showing all stored information

### Password Generation
- **Customizable Length**: Generate passwords from 1-99 characters
- **Special Characters**: Multiple special character options (!, @, #, $, %, ^, &, *, +, €, ?)
- **Uppercase Support**: Option to include uppercase letters
- **Required Text**: Include specific text requirements in generated passwords
- **Strength Indicator**: Real-time password strength analysis

### Security Features
- **Master Password Authentication**: SHA-256 hashed master password protection
- **Data Encryption**: Custom encryption algorithm for password storage
- **Secure File Handling**: Encrypted JSON storage format
- **Data Wipe Function**: Complete data removal capability

## How It Works

### Encryption Algorithm
The application uses a custom encryption algorithm inspired by AES (Advanced Encryption Standard) principles:

1. **Substitution**: Characters are replaced using a substitution table derived from the master password
2. **Transposition**: Character positions are rearranged based on the encryption key
3. **XOR Operations**: Additional security layer using XOR operations with the key
4. **SHA-256 Hashing**: Master password is hashed using SHA-256 for secure storage

### Data Storage
- **Master Password**: Stored as SHA-256 hash in `master_password.json`
- **Password Data**: Encrypted and stored in `passwords.json`
- **Local Only**: No cloud storage or external database dependencies

## Installation & Setup

### Prerequisites
- Python 3.6 or higher
- Tkinter (usually included with Python)

### Required Files
The application consists of several Python modules:
- `guiInterface.py` - Main GUI application
- `encryption.py` - Custom encryption implementation
- `fileHandler.py` - File operations and data management
- `passwordGenerator.py` - Password generation utilities

### Running the Application
```bash
python guiInterface.py
```

## Usage

### First Time Setup
1. Run the application
2. Create a master password when prompted
3. Confirm your master password
4. Start adding your password entries

### Adding Passwords
1. Enter the website name (required)
2. Optionally add username and email
3. Either generate a secure password or enter your own
4. Click "Add to List" to save

### Password Generation
1. Select desired special characters (all enabled by default)
2. Choose to include uppercase letters (enabled by default)
3. Set password length (1-99 characters)
4. Optionally add required text
5. Click "Generate Password"

### Managing Stored Passwords
- **View**: All passwords are displayed in the right panel
- **Edit**: Select an entry and click "Edit" to modify
- **Delete**: Select an entry and click "Delete" to remove
- **Refresh**: Click "Refresh" to update the display

### Security Options
- **Master Password Reset**: Delete all data and start fresh
- **Data Wipe**: Complete removal of all stored information

## File Structure

```
├── guiInterface.py          # Main GUI application
├── encryption.py            # Custom encryption algorithm
├── fileHandler.py          # File handling operations
├── passwordGenerator.py    # Password generation logic
├── master_password.json    # Encrypted master password (auto-generated)
├── passwords.json          # Encrypted password storage (auto-generated)
└── README.md              # This file
```

## Security Considerations

### Strengths
- **Offline Operation**: No internet-based vulnerabilities
- **Local Encryption**: Data encrypted before storage
- **Master Password Protection**: SHA-256 hashed authentication
- **Custom Algorithm**: Unique encryption implementation

### Best Practices
- Use a strong, unique master password
- Keep regular backups of your encrypted files
- Store the application and data files securely
- Don't share your master password

### Limitations
- **Single Device**: Not designed for multi-device synchronization
- **No Cloud Backup**: Manual backup required
- **Single User**: Designed for individual use

## Technical Details

### Password Strength Analysis
The application evaluates password strength based on:
- Length (8+ characters recommended)
- Uppercase letters
- Lowercase letters
- Numbers
- Special characters

Strength levels: Weak, Fair, Strong, Very Strong

### Encryption Process
1. Master password hashed with SHA-256
2. Password data converted to numerical values
3. Substitution cipher applied
4. Transposition performed
5. XOR operation with derived key
6. Result stored in encrypted JSON format

## Development & Testing

The encryption algorithm has been tested for:
- **Entropy Analysis**: Randomness verification
- **Security Comparison**: Benchmarked against AES principles
- **Brute Force Resistance**: Attack simulation testing

## Contributing

This is an open-source project. Feel free to:
- Report bugs or issues
- Suggest improvements
- Submit pull requests
- Fork for your own modifications

## License

[Add your chosen license here]

## Disclaimer

This password manager is designed for educational and personal use. While security measures are implemented, users should evaluate their own security requirements and consider their threat model when choosing password management solutions.

---

**Note**: Always keep backups of your encrypted password files and remember your master password. If you forget your master password, there is no recovery method and all stored data will be inaccessible.
