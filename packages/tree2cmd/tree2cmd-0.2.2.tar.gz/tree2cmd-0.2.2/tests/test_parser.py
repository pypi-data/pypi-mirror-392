import unittest
from tree2cmd.parser import clean_name, detect_indent, parse_tree


class TestParser(unittest.TestCase):

    def test_clean_name_basic(self):
        self.assertEqual(clean_name("  ├── src/"), "src")
        self.assertEqual(clean_name("📦 App/"), "📦 App")
        self.assertEqual(clean_name("  │   └── main.py"), "main.py")

    def test_detect_indent(self):
        self.assertEqual(detect_indent("    file.txt", 2), 2)
        self.assertEqual(detect_indent("  file.txt", 2), 1)
        self.assertEqual(detect_indent("\tfile.txt", 4), 1)

    def test_parse_simple_tree(self):
        text = """
        Project/
          src/
            main.py
        """
        result = parse_tree(text)

        expected = [
            ("Project", True),
            ("Project/src", True),
            ("Project/src/main.py", False)
        ]

        self.assertEqual(result, expected)

    def test_parse_with_emojis(self):
        text = """
        📦 App/
          backend/
            api.py
        """

        result = parse_tree(text)

        expected = [
            ("📦 App", True),
            ("📦 App/backend", True),
            ("📦 App/backend/api.py", False)
        ]

        self.assertEqual(result, expected)

    def test_empty_input(self):
        self.assertEqual(parse_tree(""), [])


if __name__ == "__main__":
    unittest.main()
