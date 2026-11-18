#!/usr/bin/env python3
"""Validate the patcher against user-provided original and reference IPA.

Neither file is distributed with this repository. Usage:
    python tools/verify_prepare_dylib.py ORIGINAL_DYLIB REFERENCE_IPA
"""

import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile


if len(sys.argv) != 3:
    raise SystemExit("Usage: python verify_prepare_dylib.py ORIGINAL_DYLIB REFERENCE_IPA")

ORIGINAL = pathlib.Path(sys.argv[1]).resolve()
REFERENCE = pathlib.Path(sys.argv[2]).resolve()
PATCHER = pathlib.Path(__file__).with_name("prepare_dylib.py")
sys.argv = sys.argv[:1]


class PatchVerification(unittest.TestCase):
    def invoke(self, source, target):
        return subprocess.run(
            [sys.executable, str(PATCHER), str(source), str(target)],
            capture_output=True,
            text=True,
        )

    def test_patched_file_matches_reference_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = pathlib.Path(temporary) / "patched.dylib"
            result = self.invoke(ORIGINAL, target)
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(REFERENCE) as archive:
                reference = archive.read("Payload/WeChat.app/Frameworks/WeChatIPadLogin.dylib")
            self.assertEqual(target.read_bytes(), reference)

    def test_unknown_input_is_rejected_without_creating_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = pathlib.Path(temporary) / "unknown.dylib"
            target = pathlib.Path(temporary) / "out.dylib"
            source.write_bytes(b"unrecognized input")
            result = self.invoke(source, target)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(target.exists())

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = pathlib.Path(temporary) / "out.dylib"
            target.write_bytes(b"keep this")
            result = self.invoke(ORIGINAL, target)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), b"keep this")

    def test_original_input_is_never_overwritten(self):
        before = ORIGINAL.read_bytes()
        result = self.invoke(ORIGINAL, ORIGINAL)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(ORIGINAL.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
