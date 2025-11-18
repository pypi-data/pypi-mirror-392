import unittest
from tree2cmd.cli import convert_tree_to_commands


class TestAsciiTree(unittest.TestCase):
    """Tests for ASCII tree → struct.txt conversion compatibility."""

    # ---------------------------------------------------------
    # Basic ASCII tree
    # ---------------------------------------------------------
    def test_basic_ascii_tree(self):
        text = "Project/\n" "├── src/\n" "│   └── main.py\n" "└── README.md\n"

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'mkdir -p "Project/"',
            'mkdir -p "Project/src/"',
            'touch "Project/src/main.py"',
            'touch "Project/README.md"',
        ]

        self.assertEqual(cmds, expected)

    # ---------------------------------------------------------
    # ASCII and struct.txt produce SAME output
    # ---------------------------------------------------------
    def test_ascii_vs_struct_equivalence(self):
        ascii_tree = "Project/\n" "├── src/\n" "│   └── main.py\n" "└── README.md\n"

        struct_tree = "Project/\n" "  src/\n" "    main.py\n" "  README.md\n"

        cmds_ascii = convert_tree_to_commands(ascii_tree, dry_run=True)
        cmds_struct = convert_tree_to_commands(struct_tree, dry_run=True)

        self.assertEqual(cmds_ascii, cmds_struct)

    # ---------------------------------------------------------
    # Emoji ASCII tree support
    # ---------------------------------------------------------
    def test_emoji_ascii_tree(self):
        text = "📦 App/\n" "├── backend/\n" "│   └── api.py\n" "└── README.md\n"

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'mkdir -p "📦 App/"',
            'mkdir -p "📦 App/backend/"',
            'touch "📦 App/backend/api.py"',
            'touch "📦 App/README.md"',
        ]

        self.assertEqual(cmds, expected)

    # ---------------------------------------------------------
    # ASCII tree with multiple root items
    # ---------------------------------------------------------
    def test_ascii_multiple_root(self):
        text = "Root/\n" "├── file1.txt\n" "└── file2.txt\n"

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'mkdir -p "Root/"',
            'touch "Root/file1.txt"',
            'touch "Root/file2.txt"',
        ]

        self.assertEqual(cmds, expected)

    # ---------------------------------------------------------
    # Deep nested ASCII paths
    # ---------------------------------------------------------
    def test_deep_ascii_tree(self):
        text = (
            "Project/\n"
            "├── src/\n"
            "│   ├── core/\n"
            "│   │   └── engine.py\n"
            "│   └── utils/\n"
            "│       └── helper.py\n"
            "└── README.md\n"
        )

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'mkdir -p "Project/"',
            'mkdir -p "Project/src/"',
            'mkdir -p "Project/src/core/"',
            'touch "Project/src/core/engine.py"',
            'mkdir -p "Project/src/utils/"',
            'touch "Project/src/utils/helper.py"',
            'touch "Project/README.md"',
        ]

        self.assertEqual(cmds, expected)

    def test_incomplete_ascii_tree(self):
        text = "App/\n" "├── api/\n" "    └── handler.py\n" "└── README.md\n"

        cmds = convert_tree_to_commands(text, dry_run=True)

        expected = [
            'mkdir -p "App/"',
            'mkdir -p "App/api/"',
            'touch "App/api/handler.py"',
            'touch "App/README.md"',
        ]

        self.assertEqual(cmds, expected)


if __name__ == "__main__":
    unittest.main()
