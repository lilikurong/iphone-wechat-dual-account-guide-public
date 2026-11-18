#!/usr/bin/env python3
"""Patch a specific externally supplied WeChatIPadLogin dylib for a diagnostic test.

This does not build or distribute an app. It only accepts the exact binary used
in the documented experiment and writes a new file; it never modifies input.
"""

import argparse
import hashlib
from pathlib import Path


INPUT_SHA256 = "d9b688c98c514c48289e46c3e633919646622d26c59d9b975c02a8deec991f73"
NOP = bytes.fromhex("1f 20 03 d5")
PATCHES = {
    0xBA28: bytes.fromhex("ff 00 00 94"),
    0xBA4C: bytes.fromhex("f6 00 00 94"),
    0xBA70: bytes.fromhex("ed 00 00 94"),
    0x1FA30: bytes.fromhex("1a 01 00 94"),
    0x1FA64: bytes.fromhex("0d 01 00 94"),
    0x1FA9C: bytes.fromhex("ff 00 00 94"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Original WeChatIPadLogin.dylib")
    parser.add_argument("output", type=Path, help="New output path; must not exist")
    args = parser.parse_args()

    try:
        if args.input.resolve() == args.output.resolve():
            parser.error("Input and output must be different files.")
        original = args.input.read_bytes()
        digest = hashlib.sha256(original).hexdigest()
        if digest != INPUT_SHA256:
            parser.error("Unrecognized input SHA-256; no output was written.")
        for offset, expected in PATCHES.items():
            if original[offset:offset + 4] != expected:
                parser.error(f"Unexpected instruction at 0x{offset:X}; no output was written.")

        patched = bytearray(original)
        for offset in PATCHES:
            patched[offset:offset + 4] = NOP

        # Exclusive creation also prevents overwriting an existing output file.
        with args.output.open("xb") as output:
            output.write(patched)
    except OSError as error:
        parser.error(str(error))

    print("Output SHA-256:", hashlib.sha256(patched).hexdigest().upper())


if __name__ == "__main__":
    main()
