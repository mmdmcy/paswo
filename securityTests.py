# security properties of the vault format: tamper detection, no key/nonce
# reuse, authenticated header, and a sanity check that the legacy cipher
# really is as weak as its label says.
# run: python -m unittest securityTests

import base64
import json
import os
import unittest

import encryption
from encryption import WrongPasswordOrTampered, decryptVault, encryptVault, parseVaultHeader

MASTER = "throwaway-master-9F2k"
SAMPLE = {"site": {"username": "u", "email": "e@x", "password": "s3cret-€"}}


def _flipByte(data, index):
    mutable = bytearray(data)
    mutable[index] ^= 0x01
    return bytes(mutable)


class FastScrypt(unittest.TestCase):
    def setUp(self):
        self._n = encryption.SCRYPT_N
        encryption.SCRYPT_N = 2 ** 14

    def tearDown(self):
        encryption.SCRYPT_N = self._n


class TestTamperDetection(FastScrypt):
    def _document(self):
        return json.loads(encryptVault(SAMPLE, MASTER))

    def _expectTampered(self, document):
        with self.assertRaises(WrongPasswordOrTampered):
            decryptVault(json.dumps(document).encode("utf-8"), MASTER)

    def testCiphertextBitFlipDetected(self):
        document = self._document()
        ciphertext = base64.b64decode(document["ciphertext"])
        for index in (0, len(ciphertext) // 2, len(ciphertext) - 1):
            tampered = dict(document)
            tampered["ciphertext"] = base64.b64encode(_flipByte(ciphertext, index)).decode()
            self._expectTampered(tampered)

    def testTruncatedCiphertextDetected(self):
        document = self._document()
        ciphertext = base64.b64decode(document["ciphertext"])
        document["ciphertext"] = base64.b64encode(ciphertext[:-1]).decode()
        self._expectTampered(document)

    def testNonceChangeDetected(self):
        document = self._document()
        nonce = base64.b64decode(document["nonce"])
        document["nonce"] = base64.b64encode(_flipByte(nonce, 0)).decode()
        self._expectTampered(document)

    def testSaltChangeDetected(self):
        document = self._document()
        salt = base64.b64decode(document["kdf"]["salt"])
        document["kdf"]["salt"] = base64.b64encode(_flipByte(salt, 3)).decode()
        self._expectTampered(document)

    def testKdfParameterDowngradeDetected(self):
        # the header is associated data: weakening scrypt cannot go unnoticed
        document = self._document()
        document["kdf"]["n"] = 2
        self._expectTampered(document)
        document = self._document()
        document["kdf"]["r"] = 1
        self._expectTampered(document)

    def testCiphertextSwapBetweenVaultsDetected(self):
        # ciphertext from one vault under the header of another
        documentA = self._document()
        documentB = json.loads(encryptVault({"other": "x"}, MASTER))
        documentA["ciphertext"] = documentB["ciphertext"]
        self._expectTampered(documentA)


class TestRandomness(FastScrypt):
    def testFreshSaltAndNonceEveryWrite(self):
        seen = set()
        for _ in range(5):
            header, nonce, ciphertext = parseVaultHeader(encryptVault(SAMPLE, MASTER))
            salt = header["kdf"]["salt"]
            self.assertNotIn(salt, seen)
            self.assertNotIn(nonce, seen)
            seen.add(salt)
            seen.add(nonce)

    def testSamePlaintextDifferentCiphertext(self):
        _, _, first = parseVaultHeader(encryptVault(SAMPLE, MASTER))
        _, _, second = parseVaultHeader(encryptVault(SAMPLE, MASTER))
        self.assertNotEqual(first, second)

    def testPasswordGeneratorUsesSystemRandom(self):
        import passwordGenerator
        import secrets
        self.assertIsInstance(passwordGenerator.random, secrets.SystemRandom)


class TestLegacyCipherIsWeak(unittest.TestCase):
    """Documents why legacy_cipher.py must never be used for storage."""

    def testDeterministicAndKeystreamReuse(self):
        from legacy_cipher import encryptText
        self.assertEqual(encryptText("same", "key"), encryptText("same", "key"))
        # the "three rounds" collapse to a per-position substitution with
        # period 32: equal bytes at positions 32 apart encrypt identically
        hexText = encryptText("A" * 64, "key")
        self.assertEqual(hexText[0:2], hexText[64:66])

    def testWrongPasswordNotDetected(self):
        from legacy_cipher import decryptText, encryptText
        garbage = decryptText(encryptText("hello", "right"), "wrong")
        self.assertIsInstance(garbage, str)  # silently returns junk instead of failing

    def testNonLatin1Corrupted(self):
        from legacy_cipher import decryptText, encryptText
        self.assertNotEqual(decryptText(encryptText("€", "key"), "key"), "€")


if __name__ == "__main__":
    unittest.main()
