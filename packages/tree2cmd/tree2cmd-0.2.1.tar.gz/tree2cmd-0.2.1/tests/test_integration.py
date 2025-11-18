import unittest
from tree2cmd.parser import parse_tree
from tree2cmd.cli import convert_tree_to_commands
from tree2cmd.utils import tree_from_shell_commands


class TestIntegration(unittest.TestCase):

    def test_full_pipeline(self):
        text = """
        App/
          backend/
            api.py
          frontend/
            ui.js
        """

        parsed = parse_tree(text)
        cmds = convert_tree_to_commands(text, dry_run=True)
        tree = tree_from_shell_commands(cmds)

        self.assertIn("App", tree)
        self.assertIn("backend", tree)
        self.assertIn("frontend", tree)
        self.assertIn("api.py", tree)
        self.assertIn("ui.js", tree)

        # Ensure no duplicates
        self.assertEqual(len(cmds), len(set(cmds)))

    def test_reverse_tree_count(self):
        text = """
        Root/
          a.txt
          sub/
            b.txt
        """

        cmds = convert_tree_to_commands(text, dry_run=True)
        tree = tree_from_shell_commands(cmds)

        self.assertIn("2 directories", tree)
        self.assertIn("2 files", tree)


if __name__ == "__main__":
    unittest.main()
