"""Vault file handling for paswo.

The vault is a single file, ``vault.json``, in a per-user directory:

- ``$PASWO_HOME`` if set, otherwise
- ``%LOCALAPPDATA%\\paswo`` on Windows,
- ``~/Library/Application Support/paswo`` on macOS,
- ``$XDG_DATA_HOME/paswo`` or ``~/.local/share/paswo`` elsewhere.

The directory is created with mode 0700 and the vault file with mode 0600.
Writes go to a temporary file in the same directory and are renamed over the
vault, so a crash mid-write never leaves a half-written vault behind.

Old paswo 1.0 vaults (``passwords.json`` + ``master_password.json`` next to
the script, encrypted with the insecure legacy cipher) are detected and can
be migrated once with migrateLegacyVault(); see legacy_cipher.py.
"""

import ast
import hmac
import json
import os
import shutil
import sys
import time

from encryption import VaultError, WrongPasswordOrTampered, decryptVault, encryptVault

VAULT_FILE_NAME = "vault.json"
LEGACY_PASSWORDS_FILE = "passwords.json"
LEGACY_MASTER_FILE = "master_password.json"

_IS_WINDOWS = sys.platform.startswith("win")


# ---------------------------------------------------------------------------
# locations
# ---------------------------------------------------------------------------

def getVaultDirectory():
    """Directory that holds the vault (not created here)."""
    custom = os.environ.get("PASWO_HOME")
    if custom:
        return os.path.abspath(os.path.expanduser(custom))
    if _IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "paswo")
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "paswo")
    base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "paswo")


def ensureVaultDirectory():
    """Create the vault directory with mode 0700 and return its path."""
    directory = getVaultDirectory()
    os.makedirs(directory, mode=0o700, exist_ok=True)
    if not _IS_WINDOWS:
        os.chmod(directory, 0o700)
    return directory


def getVaultPath():
    return os.path.join(getVaultDirectory(), VAULT_FILE_NAME)


def vaultExists():
    return os.path.isfile(getVaultPath())


# ---------------------------------------------------------------------------
# reading and writing
# ---------------------------------------------------------------------------

def _writePrivateFile(path, data):
    """Write bytes to path atomically with mode 0600."""
    directory = os.path.dirname(path)
    tempPath = os.path.join(directory, f".{os.path.basename(path)}.{os.getpid()}.tmp")
    descriptor = os.open(tempPath, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tempPath, path)
    except BaseException:
        try:
            os.unlink(tempPath)
        except OSError:
            pass
        raise
    if not _IS_WINDOWS:
        os.chmod(path, 0o600)


def savePasswordsToFile(passwordsDictionary, masterPasswordValue):
    """Encrypt the dictionary with the master password and write the vault."""
    if not isinstance(passwordsDictionary, dict):
        raise TypeError("passwordsDictionary must be a dict")
    ensureVaultDirectory()
    _writePrivateFile(getVaultPath(), encryptVault(passwordsDictionary, masterPasswordValue))
    return True


def loadPasswordsFromFile(masterPasswordValue):
    """Read and decrypt the vault.

    Raises FileNotFoundError if there is no vault, WrongPasswordOrTampered
    if the master password is wrong or the file was modified, and
    VaultError if the file is not a paswo vault at all.
    """
    with open(getVaultPath(), "rb") as handle:
        vaultBytes = handle.read()
    return decryptVault(vaultBytes, masterPasswordValue)


def wipeVault():
    """Delete the vault file. Returns True if nothing is left afterwards."""
    path = getVaultPath()
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
    return not os.path.exists(path)


# ---------------------------------------------------------------------------
# migration from the paswo 1.0 format (legacy cipher, two files in the CWD)
# ---------------------------------------------------------------------------

def _legacyCandidateDirectories(legacyDirectory=None):
    if legacyDirectory is not None:
        return [os.path.abspath(legacyDirectory)]
    scriptDirectory = os.path.dirname(os.path.abspath(__file__))
    candidates = [os.getcwd(), scriptDirectory]
    return list(dict.fromkeys(candidates))


def findLegacyVault(legacyDirectory=None):
    """Return the directory holding an old-format vault, or None."""
    for directory in _legacyCandidateDirectories(legacyDirectory):
        passwordsPath = os.path.join(directory, LEGACY_PASSWORDS_FILE)
        masterPath = os.path.join(directory, LEGACY_MASTER_FILE)
        if os.path.isfile(passwordsPath) and os.path.isfile(masterPath):
            if _readLegacyMasterHash(masterPath):
                return directory
    return None


def legacyVaultExists(legacyDirectory=None):
    return findLegacyVault(legacyDirectory) is not None


def _readLegacyMasterHash(masterPath):
    try:
        with open(masterPath, "r", encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(document, dict):
        return None
    storedHash = document.get("master_password_hash")
    if not isinstance(storedHash, str) or len(storedHash) != 64:
        return None
    return storedHash.lower()


def _parseLegacyEntry(decryptedText):
    """Old entries were json.dumps(dict), str(dict), or a bare password."""
    value = decryptedText
    for _ in range(3):
        if isinstance(value, dict):
            break
        if not isinstance(value, str):
            break
        try:
            value = json.loads(value)
            continue
        except ValueError:
            pass
        try:
            value = ast.literal_eval(value)
            continue
        except (ValueError, SyntaxError):
            break
    if isinstance(value, dict) and "password" in value:
        return {
            "username": str(value.get("username", "")),
            "email": str(value.get("email", "")),
            "password": str(value["password"]),
        }
    return decryptedText


def migrateLegacyVault(masterPasswordValue, legacyDirectory=None):
    """One-time migration of an old-format vault to the new format.

    Verifies the master password against the old SHA-256 hash file,
    decrypts every entry with the legacy cipher, writes a new vault, reads
    it back to confirm, and finally moves the old files into a
    ``legacy-backup-<timestamp>`` folder inside the vault directory (mode
    0700/0600) so they are no longer lying in a working tree. Delete that
    folder once you are satisfied with the migrated vault; its contents are
    protected only by the insecure legacy cipher.

    Returns the migrated password dictionary.
    """
    from legacy_cipher import decryptText, hashText

    directory = findLegacyVault(legacyDirectory)
    if directory is None:
        raise FileNotFoundError("no old-format vault found")
    if vaultExists():
        raise VaultError("a new-format vault already exists; refusing to overwrite it")

    masterPath = os.path.join(directory, LEGACY_MASTER_FILE)
    passwordsPath = os.path.join(directory, LEGACY_PASSWORDS_FILE)

    storedHash = _readLegacyMasterHash(masterPath)
    if storedHash is None or not hmac.compare_digest(hashText(masterPasswordValue), storedHash):
        raise WrongPasswordOrTampered("wrong master password for the old vault")

    with open(passwordsPath, "r", encoding="utf-8") as handle:
        content = handle.read()
    encryptedEntries = json.loads(content) if content.strip() else {}
    if not isinstance(encryptedEntries, dict):
        raise VaultError("old passwords.json has an unexpected structure")

    passwordsDictionary = {}
    for siteValue, encryptedValue in encryptedEntries.items():
        if not isinstance(encryptedValue, str):
            continue
        try:
            decryptedText = decryptText(encryptedValue, masterPasswordValue)
        except (ValueError, IndexError):
            continue
        passwordsDictionary[siteValue] = _parseLegacyEntry(decryptedText)

    savePasswordsToFile(passwordsDictionary, masterPasswordValue)
    readBack = loadPasswordsFromFile(masterPasswordValue)
    if readBack != passwordsDictionary:
        raise VaultError("migrated vault did not read back correctly")

    backupDirectory = os.path.join(getVaultDirectory(), f"legacy-backup-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(backupDirectory, mode=0o700, exist_ok=True)
    for sourcePath in (masterPath, passwordsPath):
        destinationPath = os.path.join(backupDirectory, os.path.basename(sourcePath))
        shutil.move(sourcePath, destinationPath)
        if not _IS_WINDOWS:
            os.chmod(destinationPath, 0o600)
    return passwordsDictionary
