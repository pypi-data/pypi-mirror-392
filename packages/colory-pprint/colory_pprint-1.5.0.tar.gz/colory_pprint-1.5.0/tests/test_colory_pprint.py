import io
import sys
import unittest
from colory_pprint import ColoryPPrint  # Import your updated class

class TestColoryPPrint(unittest.TestCase):
    def setUp(self):
        self.log = ColoryPPrint(debug=True)
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output  # Redirect stdout

    def tearDown(self):
        sys.stdout = sys.__stdout__  # Reset stdout

    def test_default_logging(self):
        data = {"message": "Test"}
        self.log(data)
        output = self.captured_output.getvalue()
        self.assertIn('"message": "Test"', output)  # Check content (ignoring color codes)
        self.assertTrue(output.endswith('\n'))  # Default end

    def test_custom_end(self):
        data = {"message": "Test"}
        self.log(data, end="|")
        output = self.captured_output.getvalue()
        self.assertIn('"message": "Test"', output)
        self.assertTrue(output.endswith('|'))  # Custom end

    def test_chaining_with_end(self):
        data = {"status": "error"}
        self.log.red.bold(data, end=" ")
        output = self.captured_output.getvalue()
        self.assertIn('"status": "error"', output)
        self.assertTrue(output.endswith(' '))  # End after chained styles

    def test_non_serializable_object(self):
        class NonSerializable:
            pass
        data = {"obj": NonSerializable()}
        self.log(data)
        output = self.captured_output.getvalue()
        self.assertIn('<NonSerializable object at', output)  # Handles repr

    def test_invalid_attribute(self):
        with self.assertRaises(AttributeError):
            self.log.invalid_attr({"message": "Test"})

if __name__ == '__main__':
    unittest.main()