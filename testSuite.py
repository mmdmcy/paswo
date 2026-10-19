# integration tests: vault file storage, file permissions, migration from the
# paswo 1.0 format, and the password generator.
# run: python -m unittest testSuite

import json
import os
import stat
import sys
import tempfile
import unittest

import encryption
import fileHandler
from encryption import VaultError, WrongPasswordOrTampered
from fileHandler import (findLegacyVault, legacyVaultExists, loadPasswordsFromFile,
                         migrateLegacyVault, savePasswordsToFile, vaultExists, wipeVault)
from passwordGenerator import generatePasswordString

MASTER = "throwaway-master-Zq7!"
SAMPLE = {
    "github.com": {"username": "octocat", "email": "o@example.com", "password": "hunter2€"},
    "mail.example": {"username": "", "email": "me@example.com", "password": "läuft 漢字"},
}
POSIX = not sys.platform.startswith("win")


class VaultInTempDir(unittest.TestCase):
    def setUp(self):
        self._n = encryption.SCRYPT_N
        encryption.SCRYPT_N = 2 ** 14
        self.tempDirectory = tempfile.TemporaryDirectory()
        self._oldHome = os.environ.get("PASWO_HOME")
        os.environ["PASWO_HOME"] = os.path.join(self.tempDirectory.name, "home")

    def tearDown(self):
        encryption.SCRYPT_N = self._n
        if self._oldHome is None:
            os.environ.pop("PASWO_HOME", None)
        else:
            os.environ["PASWO_HOME"] = self._oldHome
        self.tempDirectory.cleanup()


class TestVaultStorage(VaultInTempDir):
    def testSaveAndLoad(self):
        self.assertFalse(vaultExists())
        self.assertTrue(savePasswordsToFile(SAMPLE, MASTER))
        self.assertTrue(vaultExists())
        self.assertEqual(loadPasswordsFromFile(MASTER), SAMPLE)

    def testVaultLivesInPaswoHome(self):
        savePasswordsToFile(SAMPLE, MASTER)
        self.assertEqual(os.path.dirname(fileHandler.getVaultPath()), os.environ["PASWO_HOME"])
        self.assertFalse(os.path.exists(os.path.join(os.getcwd(), "vault.json")))

    @unittest.skipUnless(POSIX, "POSIX permissions")
    def testPermissions(self):
        savePasswordsToFile(SAMPLE, MASTER)
        directoryMode = stat.S_IMODE(os.stat(fileHandler.getVaultDirectory()).st_mode)
        fileMode = stat.S_IMODE(os.stat(fileHandler.getVaultPath()).st_mode)
        self.assertEqual(directoryMode, 0o700)
        self.assertEqual(fileMode, 0o600)

    def testWrongPasswordFailsCleanly(self):
        savePasswordsToFile(SAMPLE, MASTER)
        with self.assertRaises(WrongPasswordOrTampered):
            loadPasswordsFromFile("not the password")

    def testTamperedFileDetected(self):
        savePasswordsToFile(SAMPLE, MASTER)
        path = fileHandler.getVaultPath()
        with open(path, "r", encoding="utf-8") as handle:
            document = json.load(handle)
        ciphertext = bytearray(__import__("base64").b64decode(document["ciphertext"]))
        ciphertext[5] ^= 0xFF
        document["ciphertext"] = __import__("base64").b64encode(bytes(ciphertext)).decode()
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(document, handle)
        with self.assertRaises(WrongPasswordOrTampered):
            loadPasswordsFromFile(MASTER)

    def testOverwriteKeepsLatest(self):
        savePasswordsToFile(SAMPLE, MASTER)
        updated = dict(SAMPLE)
        updated["new.example"] = {"username": "n", "email": "", "password": "x"}
        savePasswordsToFile(updated, MASTER)
        self.assertEqual(loadPasswordsFromFile(MASTER), updated)
        leftovers = [name for name in os.listdir(fileHandler.getVaultDirectory()) if name.endswith(".tmp")]
        self.assertEqual(leftovers, [])

    def testMissingVault(self):
        with self.assertRaises(FileNotFoundError):
            loadPasswordsFromFile(MASTER)

    def testWipe(self):
        savePasswordsToFile(SAMPLE, MASTER)
        self.assertTrue(wipeVault())
        self.assertFalse(vaultExists())
        self.assertTrue(wipeVault())  # idempotent


class TestLegacyMigration(VaultInTempDir):
    """Builds a paswo 1.0 vault with the legacy cipher and migrates it."""

    def setUp(self):
        super().setUp()
        from legacy_cipher import encryptText, hashText
        self.legacyDirectory = os.path.join(self.tempDirectory.name, "old")
        os.makedirs(self.legacyDirectory)
        self.legacyMaster = "oldMaster123"
        # 1.0 stored the hash of the exact password string, unsalted
        with open(os.path.join(self.legacyDirectory, "master_password.json"), "w", encoding="utf-8") as handle:
            handle.write('{\n  "master_password_hash": "%s"\n}' % hashText(self.legacyMaster))
        self.legacyEntries = {
            "site-a": {"username": "ua", "email": "ea", "password": "pa"},
            "site-b": {"username": "", "email": "", "password": "pb!#"},
        }
        encrypted = {
            site: encryptText(json.dumps(data), self.legacyMaster)
            for site, data in self.legacyEntries.items()
        }
        # a pre-1.0 entry: a bare password string
        encrypted["site-c"] = encryptText("barepassword", self.legacyMaster)
        with open(os.path.join(self.legacyDirectory, "passwords.json"), "w", encoding="utf-8") as handle:
            json.dump(encrypted, handle, indent=2)

    def testDetectsLegacyVault(self):
        self.assertTrue(legacyVaultExists(self.legacyDirectory))
        self.assertEqual(findLegacyVault(self.legacyDirectory), self.legacyDirectory)
        self.assertFalse(legacyVaultExists(self.tempDirectory.name))

    def testWrongPasswordRefused(self):
        with self.assertRaises(WrongPasswordOrTampered):
            migrateLegacyVault("wrong", self.legacyDirectory)
        self.assertFalse(vaultExists())
        self.assertTrue(legacyVaultExists(self.legacyDirectory))  # nothing touched

    def testMigration(self):
        migrated = migrateLegacyVault(self.legacyMaster, self.legacyDirectory)
        expected = dict(self.legacyEntries)
        expected["site-c"] = "barepassword"
        self.assertEqual(migrated, expected)
        # the new vault is in PASWO_HOME and opens with the same password
        self.assertTrue(vaultExists())
        self.assertEqual(loadPasswordsFromFile(self.legacyMaster), expected)
        # the old files are gone from the working directory...
        self.assertFalse(legacyVaultExists(self.legacyDirectory))
        self.assertFalse(os.path.exists(os.path.join(self.legacyDirectory, "passwords.json")))
        # ...and parked in a private backup folder inside the vault directory
        backups = [name for name in os.listdir(fileHandler.getVaultDirectory()) if name.startswith("legacy-backup-")]
        self.assertEqual(len(backups), 1)
        backupDirectory = os.path.join(fileHandler.getVaultDirectory(), backups[0])
        self.assertEqual(sorted(os.listdir(backupDirectory)), ["master_password.json", "passwords.json"])
        if POSIX:
            self.assertEqual(stat.S_IMODE(os.stat(backupDirectory).st_mode), 0o700)
            for name in os.listdir(backupDirectory):
                self.assertEqual(stat.S_IMODE(os.stat(os.path.join(backupDirectory, name)).st_mode), 0o600)

    def testRefusesToOverwriteNewVault(self):
        savePasswordsToFile({"keep": "me"}, MASTER)
        with self.assertRaises(VaultError):
            migrateLegacyVault(self.legacyMaster, self.legacyDirectory)
        self.assertEqual(loadPasswordsFromFile(MASTER), {"keep": "me"})


class TestPasswordGeneration(unittest.TestCase):
    def testLengthAndCharacterSets(self):
        cases = [("", False, 8), ("!@#", False, 12), ("", True, 10), ("$%&€", True, 16), ("", True, 1)]
        for specials, uppercase, length in cases:
            password = generatePasswordString(specials, uppercase, length)
            self.assertEqual(len(password), length, (specials, uppercase, length))
            allowed = set("abcdefghijklmnopqrstuvwxyz0123456789" + specials)
            if uppercase:
                allowed |= set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            self.assertTrue(set(password) <= allowed, password)

    def testOptions(self):
        password = generatePasswordString("!?", True, 20, exclude_similar=True, exclude_chars="ab",
                                          minUppercase=2, minDigits=2, minSpecial=2)
        self.assertEqual(len(password), 20)
        self.assertFalse(set(password) & set("Il1O0ab"))
        self.assertGreaterEqual(sum(c.isupper() for c in password), 2)
        self.assertGreaterEqual(sum(c.isdigit() for c in password), 2)
        self.assertGreaterEqual(sum(c in "!?" for c in password), 2)
        dashed = generatePasswordString("", False, 12, useDashes=True, dashSpacing=4)
        self.assertEqual(dashed.count("-"), 2)
        self.assertIn("req", generatePasswordString("", False, 10, requiredText="req"))

    def testNotRepeating(self):
        self.assertNotEqual(generatePasswordString("!", True, 24), generatePasswordString("!", True, 24))


if __name__ == "__main__":
    unittest.main()
