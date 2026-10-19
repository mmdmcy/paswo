# paswo

A small offline password manager with a Tkinter GUI. Your entries are kept in
one encrypted vault file on your own machine; nothing talks to the network.

## Author
**mmdmcy** - Solo developer

## What it does

- Stores website, username, email and password entries behind a master
  password.
- Generates passwords (length, special characters, uppercase, required text,
  excluded characters, dashes, "exclude similar" option) using the operating
  system's secure random source.
- Shows a password strength indicator, lets you edit, delete, copy and search
  entries, and can wipe the vault.

## How the vault is protected

paswo uses standard, well-reviewed primitives from the
[`cryptography`](https://cryptography.io/) package. It does not implement its
own cipher.

- **Key derivation**: scrypt (`n=2^17, r=8, p=1`, 32-byte key) from your
  master password (UTF-8) and a random 16-byte salt. The salt is regenerated
  on every write.
- **Encryption**: AES-256-GCM with a random 12-byte nonce per write. The
  whole password dictionary is one authenticated ciphertext.
- **Header**: the file is a small JSON document with a format name, version,
  the scrypt parameters, salt, nonce and ciphertext (all binary values
  base64-encoded). The header is passed to GCM as associated data, so the
  KDF parameters and salt cannot be altered without the decryption failing.
- **Password check**: there is no separate password hash. The master password
  is correct if, and only if, the vault decrypts. A wrong password and a
  modified file both fail with the same error.
- **Location**: `$PASWO_HOME/vault.json` if `PASWO_HOME` is set, otherwise
  `~/.local/share/paswo/vault.json` (Linux), `~/Library/Application
  Support/paswo/vault.json` (macOS) or `%LOCALAPPDATA%\paswo\vault.json`
  (Windows). The directory is created with mode `0700`, the file with `0600`,
  and writes are atomic (temporary file + rename).

The original self-written "AES-inspired" cipher from paswo 1.0 is kept in
`legacy_cipher.py` **for educational purposes only**. It is insecure (no
salt, no key stretching, no nonce, no authentication, a 32-byte periodic
substitution, and it corrupts non-Latin-1 text) and is **not used for
storage**. It exists so that old vaults can be migrated once.

### Upgrading from paswo 1.0

If paswo finds the old `passwords.json` + `master_password.json` pair next to
the script (or in the current directory) and no new vault, the login screen
asks for your master password and converts the vault in place: entries are
decrypted with the legacy cipher, written to the new vault, read back to
confirm, and the old files are moved to a `legacy-backup-<timestamp>` folder
inside the vault directory. Delete that folder once you have checked that
every entry is there; its contents are protected only by the old cipher.

## Installation

Requires Python 3.9+ with Tkinter (included in most Python installs).

```bash
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # the only dependency: cryptography
python guiInterface.py
```

## Usage

1. First run: choose a master password and confirm it. An empty vault is
   created immediately, so the password you typed is the one that opens it.
2. Add entries on the left (website and password are required), or generate
   a password first.
3. Entries appear on the right. Select one to edit or delete it.
4. **Wipe All Data** on the login screen deletes the vault file. There is no
   recovery: if you forget the master password, the vault cannot be opened.

## Security notes

What the design protects against:

- Someone who copies `vault.json` (backup, stolen disk, synced folder)
  cannot read your entries or learn their number, names or lengths beyond the
  total ciphertext size, and cannot change entries without the change being
  detected on the next open.
- Guessing the master password offline is slowed down by scrypt; each guess
  costs roughly 128 MiB of memory and a noticeable fraction of a second.
  Choose a long master password anyway: the KDF buys time, not immunity.
- Other local users cannot read the vault file (`0600`) on Unix-like
  systems.

What it does **not** protect against:

- Anything running as your user while the vault is unlocked. The master
  password and every entry are plain Python strings in memory, in the
  Tkinter widgets, and (when you copy) on the clipboard. Python cannot
  reliably zero memory.
- A compromised machine: malware, keyloggers, screen capture, or a
  tampered copy of paswo itself.
- A weak master password. Length matters more than symbols.
- Loss of the vault file. Keep a backup of `vault.json`; it is safe to back
  up as-is.
- Windows file permissions: on Windows the file is created with the default
  ACLs of your profile directory, which is private to your account on a
  normal setup but is not tightened further by paswo.

paswo is a personal project and has not been audited. For anything
important, use an established password manager.

## Files

```
guiInterface.py          Tkinter GUI
encryption.py            scrypt + AES-256-GCM vault container (cryptography)
fileHandler.py           vault location, 0600/0700 permissions, atomic writes, 1.0 migration
passwordGenerator.py     password generator (secrets.SystemRandom)
legacy_cipher.py         the 1.0 cipher, educational only, used for migration
testEncryption.py        unit tests for the vault container
securityTests.py         tamper detection, nonce/salt freshness, legacy-cipher weaknesses
testSuite.py             storage, permissions, migration, generator
testPasswordStrength.py  strength indicator check
requirements.txt         cryptography
```

Run the tests with:

```bash
python -m unittest testEncryption securityTests testSuite
```

Vault files (`*.json`) are ignored by git. Never commit a vault.

## License

MIT, see `LICENSE.md`.
