# SPDX-License-Identifier: BSD-3-Clause
"""Test runner for evennia-yaml-reader.

Pure stdlib unittest — no Django, no Evennia bootstrap. This is a deliberate
divergence from sibling libraries in FCM/libraries/, justified by the library
being a pure-Python primitive with no Evennia runtime dependency. See
CLAUDE.md "Tools and environment" for the rationale.

Run with:

    python runtests.py
"""

import sys
import unittest


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName("evennia_yaml_reader.tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
