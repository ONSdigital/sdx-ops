#!/usr/bin/env python
#   coding: UTF-8

import re
import unittest

from sdx.common.config import config_parser
from sdx.common.test.test_config import CheckSafeValueTests
from sdx.ops.configure import generate_config


class ConfigTests(unittest.TestCase):

    @staticmethod
    def check_secret(val):
        r = re.compile("[0-9a-zA-Z-=]{44}")
        return r.match(val)

    def setUp(self):
        content = generate_config(secret=CheckSafeValueTests.secretString)
        self.cfg = config_parser(content)

    def test_config_needs_secret(self):
        self.assertRaises(ValueError, generate_config)
        self.assertRaises(ValueError, generate_config, None)

    def test_sdx_collect_secret(self):
        self.assertTrue(
            ConfigTests.check_secret(self.cfg["sdx.collect"]["secret"]),
            self.cfg["sdx.collect"]["secret"]
        )
        self.assertEqual(
            self.cfg["sdx.collect"]["secret"],
            CheckSafeValueTests.secretString
        )

    def test_sdx_receipt_ctp_secret(self):
        self.assertTrue(
            ConfigTests.check_secret(self.cfg["sdx.receipt.ctp"]["secret"]),
            self.cfg["sdx.receipt.ctp"]["secret"]
        )
        self.assertEqual(
            self.cfg["sdx.receipt.ctp"]["secret"],
            CheckSafeValueTests.secretString
        )

    def test_sdx_receipt_rrm_secret(self):
        self.assertTrue(
            ConfigTests.check_secret(self.cfg["sdx.receipt.rrm"]["secret"]),
            self.cfg["sdx.receipt.rrm"]["secret"]
        )
        self.assertEqual(
            self.cfg["sdx.receipt.rrm"]["secret"],
            CheckSafeValueTests.secretString
        )
