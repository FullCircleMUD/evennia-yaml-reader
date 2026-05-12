# SPDX-License-Identifier: BSD-3-Clause
"""Smoke tests for evennia-yaml-reader.

Proves the package installs and the test runner discovers tests correctly.
Real tests land alongside Reader implementations as they are extracted from
evennia-world-builder.
"""

import unittest

import evennia_yaml_reader


class PackageSmokeTest(unittest.TestCase):
    def test_version_present(self):
        self.assertEqual(evennia_yaml_reader.__version__, "0.0.1")


if __name__ == "__main__":
    unittest.main()
