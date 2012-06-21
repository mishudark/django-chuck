import os
import sys
import shutil
import unittest
from django_chuck import utils
import django_chuck.template.base
from django_chuck.subsystem.filesystem import find_commands
from django_chuck.exceptions import TemplateError
from django_chuck.settings import Settings


class UtilsTest(unittest.TestCase):

    def test_autoload_commands(self):
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        settings = Settings()
        cmds = find_commands()

        self.assertTrue(utils.autoload_commands(subparsers, settings, cmds))


    def test_get_template_engine(self):
        sys.path.insert(0, ".")
        obj = utils.get_template_engine("django_chuck/tests", "django_chuck/test/project_dir")
        self.assertTrue(issubclass(obj.__class__, django_chuck.template.base.BaseEngine))


    def test_compile_template_with_extension(self):
        shutil.copy("django_chuck/tests/templates/base.html", "django_chuck/tests/project_dir/base.html")
        placeholder = {"WHO": "Balle"}

        result = utils.compile_template("django_chuck/tests/templates/site.html", "django_chuck/tests/project_dir/site.html", placeholder, "tests", "django_chuck/tests/project_dir")
        self.assertTrue(result)
        self.assertFalse(os.path.isfile("django_chuck/tests/project_dir/site.html"))

        with open("django_chuck/tests/project_dir/base.html", "r") as f:
            content = f.read()
            self.assertTrue("<html>" in content)
            self.assertTrue("Hello Balle" in content)


    def test_compile_template_without_extension(self):
        placeholder = {"WHO": "Balle"}

        result = utils.compile_template("django_chuck/tests/templates/placeholder.html", "django_chuck/tests/project_dir/placeholder.html", placeholder, "tests", "django_chuck/tests/project_dir")
        self.assertTrue(os.path.isfile("django_chuck/tests/project_dir/placeholder.html"))

        with open("django_chuck/tests/project_dir/placeholder.html", "r") as f:
            content = f.read()
            self.assertTrue("Hello Balle" in content)


if __name__ == '__main__':
    unittest.main()
