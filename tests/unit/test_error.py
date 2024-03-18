import unittest

from osc_bsu_backup import error


class TestErrorMethods(unittest.TestCase):
    def test_input_error(self):
        self.assertEqual(error.InputError("test").message, "test")


if __name__ == "__main__":
    unittest.main()
