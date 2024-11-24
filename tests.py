import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import subprocess
import networkx as nx
from io import StringIO
import matplotlib.pyplot as plt
import tempfile
import shutil
from main import *

class TestGitDependencyGraph(unittest.TestCase):

    def setUp(self):
        self.repo_dir = tempfile.mkdtemp()
        self.target_file = "test_file.txt"
        self.output_file = os.path.join(self.repo_dir, "output_graph.png")
        test_file_path = os.path.join(self.repo_dir, self.target_file)
        with open(test_file_path, "w") as f:
            f.write("Test content")
        subprocess.run(["git", "init"], cwd=self.repo_dir)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo_dir)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.repo_dir)
        subprocess.run(["git", "add", self.target_file], cwd=self.repo_dir)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.repo_dir)
        with open(test_file_path, "a") as f:
            f.write("\nMore content")
        subprocess.run(["git", "commit", "-am", "Updated test file"], cwd=self.repo_dir)

    def tearDown(self):
        shutil.rmtree(self.repo_dir)

    def test_get_commits_with_file(self):
        commits = get_commits_with_file(self.repo_dir, self.target_file)
        self.assertEqual(len(commits), 2)
        self.assertIn("Initial commit", [commit[1] for commit in commits])
        self.assertIn("Updated test file", [commit[1] for commit in commits])

    def test_build_dependency_graph(self):
        commits = [
            ("hash1", "Commit 1"),
            ("hash2", "Commit 2"),
        ]
        build_dependency_graph(self.repo_dir, commits, self.output_file)
        self.assertTrue(os.path.exists(self.output_file))

    @patch("subprocess.run")
    def test_get_commits_with_file_mocked(self, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(
            stdout="hash1 Commit 1\n\nfile1\nhash2 Commit 2\n\nfile2\n",
            returncode=0,
        )
        commits = get_commits_with_file(self.repo_dir, "file1")
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0][0], "hash1")
        self.assertEqual(commits[0][1], "Commit 1")

    def test_empty_repository(self):
        empty_repo_dir = tempfile.mkdtemp()
        subprocess.run(["git", "init"], cwd=empty_repo_dir)
        commits = get_commits_with_file(empty_repo_dir, self.target_file)
        self.assertEqual(len(commits), 0)
        shutil.rmtree(empty_repo_dir)


if __name__ == "__main__":
    unittest.main()
