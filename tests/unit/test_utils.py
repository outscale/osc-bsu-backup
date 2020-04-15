import unittest
import osc_bsu_backup.utils as utils
import logging


class TestUtilsMethods(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_setup_logging1(self):
        self.assertIsInstance(utils.setup_logging(), logging.RootLogger)
    def test_setup_logging2(self):
        self.assertIsInstance(utils.setup_logging("aaa"), logging.Logger)
    def test_setup_logging3(self):
        self.assertEqual(
            utils.setup_logging("aaa", logging.DEBUG).getEffectiveLevel(), logging.DEBUG
        )
    def test_setup_logging4(self):
        self.assertEqual(
            utils.setup_logging("aaa", logging.INFO).getEffectiveLevel(), logging.INFO
        )


if __name__ == "__main__":
    unittest.main()
