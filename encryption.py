"""Vault encryption for paswo: scrypt key derivation + AES-256-GCM.

Everything here goes through the ``cryptography`` package; nothing is
hand-rolled. The container format (version 1) is a small JSON document so a
vault file stays inspectable with a text editor, but every value that
matters is binary and base64-encoded:

    {
      "format": "paswo-vault",
      "version": 1,
      "kdf": {"name": "scrypt", "n": 131072, "r": 8, "p": 1, "salt": "..."},
      "cipher": "AES-256-GCM",
      "nonce": "...",
      "ciphertext": "..."
    }

- The 32-byte key is derived from the master password (UTF-8) with scrypt
  and a fresh random 16-byte salt per write.
- The payload (UTF-8 JSON of the password dictionary) is encrypted with
  AES-256-GCM under a fresh random 12-byte nonce per write.
- The header fields (format, version, kdf parameters, salt, cipher) are
  passed to GCM as associated data, so an attacker cannot weaken the KDF
  parameters or swap the salt without the tag check failing.
- Verifying the master password is simply a successful authenticated
  decryption: a wrong password and a tampered file both raise
  WrongPasswordOrTampered. There is no separate password hash file.
"""

import base64
import json
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

VAULT_FORMAT = "paswo-vault"
VAULT_VERSION = 1
CIPHER_NAME = "AES-256-GCM"
KDF_NAME = "scrypt"

# scrypt work factor: n=2**17, r=8, p=1 needs ~128 MiB and a fraction of a
# second on a modern machine. Parameters are stored in the vault header, so
# they can be raised later without breaking existing vaults.
SCRYPT_N = 2 ** 17
SCRYPT_R = 8
SCRYPT_P = 1
SALT_BYTES = 16
NONCE_BYTES = 12
KEY_BYTES = 32


class VaultError(Exception):
    """The file is not a paswo vault, or has an unsupported version."""


class WrongPasswordOrTampered(VaultError):
    """Authenticated decryption failed: wrong master password or modified file."""


def _b64encode(rawBytes):
    return base64.b64encode(rawBytes).decode("ascii")


def _b64decode(text):
    try:
        return base64.b64decode(text, validate=True)
    except (ValueError, TypeError) as error:
        raise VaultError("vault contains invalid base64 data") from error


def deriveKey(masterPassword, salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P):
    """Derive a 32-byte AES key from the master password with scrypt."""
    if not isinstance(masterPassword, str) or masterPassword == "":
        raise ValueError("master password must be a non-empty string")
    kdf = Scrypt(salt=salt, length=KEY_BYTES, n=n, r=r, p=p)
    return kdf.derive(masterPassword.encode("utf-8"))


def _associatedData(header):
    """Canonical bytes of the header, authenticated alongside the payload."""
    return json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8")


def encryptVault(passwordsDictionary, masterPassword):
    """Serialise the dictionary and return the vault file contents as bytes."""
    salt = os.urandom(SALT_BYTES)
    nonce = os.urandom(NONCE_BYTES)
    header = {
        "format": VAULT_FORMAT,
        "version": VAULT_VERSION,
        "kdf": {
            "name": KDF_NAME,
            "n": SCRYPT_N,
            "r": SCRYPT_R,
            "p": SCRYPT_P,
            "salt": _b64encode(salt),
        },
        "cipher": CIPHER_NAME,
    }
    kdf = header["kdf"]
    key = deriveKey(masterPassword, salt, n=kdf["n"], r=kdf["r"], p=kdf["p"])
    plaintext = json.dumps(passwordsDictionary, ensure_ascii=False).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, _associatedData(header))

    document = dict(header)
    document["nonce"] = _b64encode(nonce)
    document["ciphertext"] = _b64encode(ciphertext)
    return (json.dumps(document, indent=2) + "\n").encode("utf-8")


def parseVaultHeader(vaultBytes):
    """Return (header, nonce, ciphertext) or raise VaultError.

    Checks the structure only; nothing is decrypted.
    """
    try:
        document = json.loads(vaultBytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        raise VaultError("file is not a paswo vault (not valid JSON)") from error
    if not isinstance(document, dict) or document.get("format") != VAULT_FORMAT:
        raise VaultError("file is not a paswo vault")
    if document.get("version") != VAULT_VERSION:
        raise VaultError(f"unsupported vault version: {document.get('version')!r}")
    if document.get("cipher") != CIPHER_NAME:
        raise VaultError(f"unsupported cipher: {document.get('cipher')!r}")
    kdf = document.get("kdf")
    if not isinstance(kdf, dict) or kdf.get("name") != KDF_NAME:
        raise VaultError("unsupported key derivation function")
    for parameter in ("n", "r", "p"):
        if not isinstance(kdf.get(parameter), int) or kdf[parameter] <= 0:
            raise VaultError(f"invalid scrypt parameter {parameter!r}")
    header = {
        "format": document["format"],
        "version": document["version"],
        "kdf": {
            "name": kdf["name"],
            "n": kdf["n"],
            "r": kdf["r"],
            "p": kdf["p"],
            "salt": kdf.get("salt"),
        },
        "cipher": document["cipher"],
    }
    salt = _b64decode(header["kdf"]["salt"] or "")
    nonce = _b64decode(document.get("nonce") or "")
    ciphertext = _b64decode(document.get("ciphertext") or "")
    if len(salt) != SALT_BYTES or len(nonce) != NONCE_BYTES:
        raise VaultError("vault has a malformed salt or nonce")
    return header, nonce, ciphertext


def decryptVault(vaultBytes, masterPassword):
    """Decrypt vault file contents and return the password dictionary.

    Raises VaultError if the file is not a vault, and
    WrongPasswordOrTampered if the password is wrong or the file was
    modified (the two cases are indistinguishable by design).
    """
    header, nonce, ciphertext = parseVaultHeader(vaultBytes)
    kdf = header["kdf"]
    salt = _b64decode(kdf["salt"])
    try:
        key = deriveKey(masterPassword, salt, n=kdf["n"], r=kdf["r"], p=kdf["p"])
    except ValueError:
        # empty password or scrypt rejected the parameters
        raise WrongPasswordOrTampered("wrong master password or tampered vault")
    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, _associatedData(header))
    except InvalidTag:
        raise WrongPasswordOrTampered("wrong master password or tampered vault") from None
    try:
        passwordsDictionary = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        raise VaultError("vault payload is not valid JSON") from error
    if not isinstance(passwordsDictionary, dict):
        raise VaultError("vault payload is not a dictionary")
    return passwordsDictionary
