import unittest
from tree2cmd.cli import convert_tree_to_commands


class TestCLI(unittest.TestCase):
    """Tests for the CLI converter using real struct.txt-style examples."""

    # ---------------------------------------------------------
    # Basic project tree
    # ---------------------------------------------------------
    def test_basic_tree(self):
        text = "Project/\n" "  src/\n" "    main.py\n" "  README.md\n"

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'mkdir -p "Project/"',
            'mkdir -p "Project/src/"',
            'touch "Project/src/main.py"',
            'touch "Project/README.md"',
        ]

        self.assertEqual(cmds, expected)

    # ---------------------------------------------------------
    # Emoji project tree
    # ---------------------------------------------------------
    def test_with_emojis(self):
        text = "📦 App/\n" "  backend/\n" "    api.py\n" "  README.md\n"

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'mkdir -p "📦 App/"',
            'mkdir -p "📦 App/backend/"',
            'touch "📦 App/backend/api.py"',
            'touch "📦 App/README.md"',
        ]

        self.assertEqual(cmds, expected)

    # ---------------------------------------------------------
    # Single file
    # ---------------------------------------------------------
    def test_single_file(self):
        text = "hello.txt\n"
        cmds = convert_tree_to_commands(text, dry_run=True)
        self.assertEqual(cmds, ['touch "hello.txt"'])

    # ---------------------------------------------------------
    # Single folder
    # ---------------------------------------------------------
    def test_single_folder(self):
        text = "folder/\n"
        cmds = convert_tree_to_commands(text, dry_run=True)
        self.assertEqual(cmds, ['mkdir -p "folder/"'])

    # ---------------------------------------------------------
    # Empty struct
    # ---------------------------------------------------------
    def test_empty(self):
        cmds = convert_tree_to_commands("", dry_run=True)
        self.assertEqual(cmds, [])

    # ---------------------------------------------------------
    # Mixed spacing (spaces + tabs)
    # ---------------------------------------------------------
    def test_mixed_indentation(self):
        text = "Project/\n" "    sub/\n" "\t\tfile.txt\n"

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'mkdir -p "Project/"',
            'mkdir -p "Project/sub/"',
            'touch "Project/sub/file.txt"',
        ]

        self.assertEqual(cmds, expected)

    # ---------------------------------------------------------
    # Root-level multiple items
    # ---------------------------------------------------------
    def test_multiple_root_items(self):
        text = "A.txt\n" "B.txt\n"

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'touch "A.txt"',
            'touch "B.txt"',
        ]

        self.assertEqual(cmds, expected)


if __name__ == "__main__":
    unittest.main()
