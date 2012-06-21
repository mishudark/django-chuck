import os
import unittest
from django_chuck.subsystem.filesystem import get_files, write_to_file, append_to_file, find_chuck_module_path, find_chuck_command_path, find_commands


class FilesystemTest(unittest.TestCase):
    def setUp(self):
        self.test_file = os.path.join("django_chuck", "tests", "project_dir", "test_file")

        if os.path.isfile(self.test_file):
            os.unlink(self.test_file)

    def test_get_files(self):
        files = get_files(os.curdir)
        self.assertTrue(len(files) > 0)

        for file in files:
            self.assertTrue(os.path.isfile(file), "File " + file)


    def test_write_to_file(self):
        test_data = "some wicked cool stuff"
        write_to_file(self.test_file, test_data)

        with open(self.test_file, "r") as f:
            self.assertEqual(f.read(), test_data)


    def test_append_to_file(self):
        test_data = "some wicked cool stuff"
        test_data2 = "even more test data"

        write_to_file(self.test_file, test_data)
        append_to_file(self.test_file, test_data2)

        with open(self.test_file, "r") as f:
            self.assertEqual(f.read(), test_data + test_data2)


    def test_find_chuck_module_path(self):
        self.assertTrue(os.path.exists(find_chuck_module_path()))


    def test_find_chuck_command_path(self):
        self.assertTrue(os.path.exists(find_chuck_command_path()))


    def test_find_commands(self):
        self.assertTrue(len(find_commands()) > 0)


if __name__ == '__main__':
    unittest.main()
