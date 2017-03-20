import unittest

from sdx.common.processor import Processor


class ProcessorTests(unittest.TestCase):

    def test_processor_unsigned(self):
        proc = Processor.unsigned_integer

        # Supply int default for range checking
        self.assertEqual(0, proc("q", {"q": -1}, 0))
        self.assertEqual(0, proc("q", {"q": 0}, 0))
        self.assertEqual(1, proc("q", {"q": 1}, 0))
        self.assertEqual(100, proc("q", {"q": 1E2}, 0))
        self.assertEqual(1000000000, proc("q", {"q": 1E9}, 0))

        # Supply bool default for range checking and type coercion
        self.assertIs(False, proc("q", {"q": -1}, False))
        self.assertIs(False, proc("q", {"q": 0}, False))
        self.assertIs(True, proc("q", {"q": 1}, False))
        self.assertIs(True, proc("q", {"q": 1E2}, False))
        self.assertIs(True, proc("q", {"q": 1E9}, False))
        self.assertIs(False, proc("q", {"q": 0}, False))

    def test_processor_percentage(self):
        proc = Processor.percentage

        # Supply int default for range checking
        self.assertEqual(0, proc("q", {"q": -1}, 0))
        self.assertEqual(0, proc("q", {"q": 0}, 0))
        self.assertEqual(100, proc("q", {"q": 100}, 0))
        self.assertEqual(0, proc("q", {"q": 0}, 0))

        # Supply bool default for range checking and type coercion
        self.assertIs(False, proc("q", {"q": -1}, False))
        self.assertIs(False, proc("q", {"q": 0}, False))
        self.assertIs(True, proc("q", {"q": 100}, False))
        self.assertIs(False, proc("q", {"q": 0}, False))
