# unit tests for encryption.py (scrypt + AES-256-GCM vault container)
# run: python -m unittest testEncryption

import json
import unittest

import encryption
from encryption import (VaultError, WrongPasswordOrTampered, decryptVault,
                        encryptVault, parseVaultHeader)

# throwaway values only
MASTER = "correct horse battery staple"
SAMPLE = {
    "example.com": {"username": "alice", "email": "a@example.com", "password": "p4ss-w0rd!"},
    "ünïcödé.example": {"username": "bób", "email": "", "password": "pässwörd€漢字🔐"},
    "old-style-entry": "just-a-string",
}


class FastScrypt(unittest.TestCase):
    """Use a smaller scrypt work factor so the suite runs quickly.

    The parameters are stored in the vault header, so decryption still works
    with whatever was used at write time; testRealParameters covers the
    production values.
    """

    def setUp(self):
        self._n = encryption.SCRYPT_N
        encryption.SCRYPT_N = 2 ** 14

    def tearDown(self):
        encryption.SCRYPT_N = self._n


class TestRoundTrip(FastScrypt):
    def testRoundTrip(self):
        blob = encryptVault(SAMPLE, MASTER)
        self.assertEqual(decryptVault(blob, MASTER), SAMPLE)

    def testUnicodeSurvives(self):
        data = {"site": {"username": "", "email": "", "password": "€ ÿ 漢字 🔐 \u0000"}}
        self.assertEqual(decryptVault(encryptVault(data, "pässwörd€"), "pässwörd€"), data)

    def testEmptyVault(self):
        self.assertEqual(decryptVault(encryptVault({}, MASTER), MASTER), {})

    def testHeaderIsReadableWithoutPassword(self):
        header, nonce, ciphertext = parseVaultHeader(encryptVault(SAMPLE, MASTER))
        self.assertEqual(header["format"], "paswo-vault")
        self.assertEqual(header["version"], 1)
        self.assertEqual(header["cipher"], "AES-256-GCM")
        self.assertEqual(header["kdf"]["name"], "scrypt")
        self.assertEqual(len(nonce), 12)
        self.assertGreater(len(ciphertext), 16)  # at least the GCM tag

    def testFileIsPlainJsonWithNoPlaintext(self):
        blob = encryptVault(SAMPLE, MASTER)
        document = json.loads(blob.decode("utf-8"))
        self.assertEqual(set(document), {"format", "version", "kdf", "cipher", "nonce", "ciphertext"})
        for secret in ("alice", "p4ss-w0rd!", "example.com", MASTER):
            self.assertNotIn(secret.encode("utf-8"), blob)


class TestFailures(FastScrypt):
    def testWrongPasswordRaises(self):
        blob = encryptVault(SAMPLE, MASTER)
        with self.assertRaises(WrongPasswordOrTampered):
            decryptVault(blob, MASTER + "x")

    def testEmptyPasswordRejectedOnEncrypt(self):
        with self.assertRaises(ValueError):
            encryptVault(SAMPLE, "")

    def testEmptyPasswordFailsCleanlyOnDecrypt(self):
        blob = encryptVault(SAMPLE, MASTER)
        with self.assertRaises(WrongPasswordOrTampered):
            decryptVault(blob, "")

    def testNotAVault(self):
        for junk in (b"", b"not json", b"{}", b'{"format": "something-else"}', b"\xff\xfe"):
            with self.assertRaises(VaultError):
                decryptVault(junk, MASTER)

    def testUnsupportedVersion(self):
        document = json.loads(encryptVault(SAMPLE, MASTER))
        document["version"] = 99
        with self.assertRaises(VaultError):
            decryptVault(json.dumps(document).encode(), MASTER)


class TestRealParameters(unittest.TestCase):
    def testRealParameters(self):
        blob = encryptVault({"a": "b"}, MASTER)
        header, _, _ = parseVaultHeader(blob)
        self.assertEqual(header["kdf"]["n"], 2 ** 17)
        self.assertEqual(header["kdf"]["r"], 8)
        self.assertEqual(header["kdf"]["p"], 1)
        self.assertEqual(decryptVault(blob, MASTER), {"a": "b"})


if __name__ == "__main__":
    unittest.main()
