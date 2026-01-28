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
- **User-Friendly Interface**: Clean, intuitive GUI built with Tkinter, designed for quick loading and friendly user experience.

### Password Management
- **Store Website Credentials**: Save website name, username, email, and password. No length restrictions or pop-up warnings.
- **Edit Existing Entries**: Easily modify stored credentials directly inline within the password list. Click the pencil icon next to a field to edit, and press Enter to save changes.
- **Copy Credentials**: Quickly copy website, username, email, or password to clipboard using dedicated copy icons.
- **Delete Entries**: Remove unwanted password entries without confirmation pop-ups.
- **Clear Display**: Well-organized list showing all stored information.
- **Always Visible Add Entry**: The "Add Entry" button remains visible regardless of advanced settings menu state.

### Password Generation
- **Customizable Length**: Generate passwords from 1-99 characters, with no minimum length restrictions.
- **Special Characters**: Multiple special character options (!, @, #, $, %, ^, &, *, +, €, ?) with a "Toggle All" option.
- **Uppercase Support**: Option to include uppercase letters.
- **Required Text**: Include specific text requirements in generated passwords.
- **Exclude Characters**: Specify characters to exclude from generated passwords.
- **Add Dashes**: Option to add dashes at specified intervals.
- **Exclude Similar Chars**: Option to exclude similar characters (I, l, 1, O, 0).

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
4. Click "Add Entry" to save

### Password Generation
1. Use the various options to customize your password:
   - **Length**: Set the desired length (no minimum).
   - **Special characters**: Select specific characters or use "Toggle All".
   - **Uppercase**: Include or exclude uppercase letters.
   - **Dashes**: Add dashes at regular intervals.
   - **Exclude similar chars**: Prevent similar characters (I, l, 1, O, 0).
   - **Required text**: Include specific text in the password.
   - **Exclude chars**: Specify characters to avoid.
2. Click "Generate" to create the password.

### Managing Stored Passwords
- **View**: All passwords are displayed in the main table.
- **Copy**: Click the clipboard icon (📋) next to the Website, Username, Email, or Password fields to copy their value to the clipboard.
- **Edit**: Click the pencil icon (✎) next to the Website, Username, Email, or Password fields to edit them directly in the table. Press `Enter` to save changes.
- **Delete**: Select an entry and click "Delete" to remove it without a confirmation prompt.
- **Search & Filter**: Use the search bar and filter dropdown to find specific entries.
- **Refresh**: Click "Refresh" to update the display.

### Security Options
- **Master Password Reset**: Delete all data and start fresh.
- **Data Wipe**: Complete removal of all stored information.

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

### Security Considerations

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

## Technical Architecture & Engineering Highlights

This project demonstrates a deep understanding of cryptographic principles and software engineering fundamentals by implementing core security features from scratch without relying on external cryptographic libraries.

### 🛠️ Technology Stack
- **Language**: Python 3.6+ (Strict typing, modular design)
- **GUI Framework**: Tkinter (Native Python GUI, zero external dependencies)
- **Architecture**: Modular Monolith (Separation of concerns between UI, Logic, and Data)
- **Data Persistence**: Encrypted JSON Serialization
- **Dependencies**: **Zero Runtime Dependencies** (Built entirely with Python Standard Library)

### Key Engineering Strategies
1.  **Custom Cryptographic Implementation**:
    - **SHA-256 Hashing**: Implemented a full SHA-256 algorithm from scratch for master password authentication, verifying deep knowledge of bitwise operations and hashing standards.
    - **Symmetric Encryption Engine**: Designed and implemented a custom AES-inspired encryption protocol featuring:
        - **Substitution Layers**: Dynamic S-Box generation based on key hashing.
        - **Transposition**: Key-dependent scrambling of data blocks.
        - **XOR Feistel-like Structure**: multiple rounds of mixing for diffusion and confusion.
    - **Entropy Management**: Usage of system time-based seeding for non-deterministic operations.

2.  **Zero-Dependency Architecture**:
    - The entire application runs on a standard Python installation.
    - Eliminates supply chain attack vectors associated with third-party NPM/Pip packages.
    - Ensures maximum portability across Windows, Linux, and macOS.

3.  **Local-First Security Design**:
    - **Air-Gapped Ready**: No network calls, no telemetry, no cloud sync.
    - **Memory Safety**: Critical cryptographic operations handle byte-level data explicitly.
    - **Fail-Safe Defaults**: Application defaults to "deny" (wipes data on failure/reset triggers).

### Test Coverage
- **Unit Testing**: Comprehensive test suite (`testSuite.py`) verifying the custom crypto algorithms against standard vectors.
- **Integration Testing**: Automated flows ensuring data integrity through the Encrypt -> Save -> Load -> Decrypt pipeline.

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
