import unittest
import osc_bsu_backup.utils as utils
import logging


class TestUtilsMethods(unittest.TestCase):
    def test_setup_logging(self):
        self.assertIsInstance(utils.setup_logging(), logging.RootLogger)
        self.assertIsInstance(utils.setup_logging("aaa"), logging.Logger)
        self.assertEqual(
            utils.setup_logging("aaa", logging.DEBUG).getEffectiveLevel(), logging.DEBUG
        )
        self.assertEqual(
            utils.setup_logging("aaa", logging.INFO).getEffectiveLevel(), logging.INFO
        )


if __name__ == "__main__":
    unittest.main()
