import os
import unittest
from mock import Mock
from django_chuck.commands.base import BaseCommand
from django_chuck.settings import Settings

class CommandsTest(unittest.TestCase):
    def test_inject_variables_and_functions(self):
        victim_class = type("Victim", (object,), {})
        test_class = type("Test", (BaseCommand,), {})
        self.test_obj = test_class()

        self.test_obj.settings.cfg["site_dir"] = "site_dir"
        self.test_obj.settings.cfg["project_dir"] = "project_dir"
        self.test_obj.settings.cfg["project_prefix"] = "project_prefix"
        self.test_obj.settings.cfg["project_name"] = "project_name"
        self.test_obj.settings.cfg["project_basedir"] = "project_basedir"

        victim_class = self.test_obj.inject_variables_and_functions(victim_class)

        self.assertEqual(victim_class.virtualenv_dir, "project_prefix-project_name")
        self.assertEqual(victim_class.site_dir, "project_basedir/project_prefix-project_name")
        self.assertEqual(victim_class.project_dir, "project_basedir/project_prefix-project_name/project_name")
        self.assertEqual(victim_class.project_name, "project_name")
        self.assertEqual(victim_class.site_name, "project_prefix-project_name")

        self.assertTrue(getattr(victim_class, "execute_in_project"))
        self.assertTrue(getattr(victim_class, "db_cleanup"))
        self.assertTrue(getattr(victim_class, "load_fixtures"))


if __name__ == '__main__':
    unittest.main()
