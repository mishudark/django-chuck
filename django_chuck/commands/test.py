import os
import unittest
from mock import Mock
from django_chuck.commands.base import BaseCommand


class ComandsTest(unittest.TestCase):
    def setUp(self):
        test_class = type("Test", (BaseCommand,), {})
        self.test_obj = test_class()
        self.test_obj.cfg = {}
        self.test_obj.arg = {}


    def test_arg_or_cfg(self):
        self.test_obj.arg = {}
        self.test_obj.cfg["project_name"] = "balle was here"
        self.assertEqual(self.test_obj.arg_or_cfg("project_name"), "balle was here")


    def test_insert_default_modules(self):
        self.test_obj.cfg["default_modules"] = ["tick", "trick", "track"]
        self.assertEqual(self.test_obj.insert_default_modules(["donald"]), ["core", "tick", "trick", "track", "donald"])


    def test_get_install_modules(self):
        self.test_obj.args = type("Argh", (object,), {"modules": "simpsons, futurama"})
        self.test_obj.cfg["default_modules"] = ["tick", "trick", "track"]
        self.test_obj.cfg["module_aliases"] = {"simpsons": ["homer", "marge", "bart", "lisa", "maggie"]}
        self.assertEqual(self.test_obj.get_install_modules(), ["core", "tick", "trick", "track", "homer", "marge", "bart", "lisa", "maggie", "futurama"])


    def test_get_module_cache(self):
        from django_chuck.base.modules import BaseModule

        self.test_obj.args = type("Argh", (object,), {})
        self.test_obj.cfg["module_basedirs"] = ["."]
        self.test_obj.cfg["module_basedir"] = "../../modules"

        cache = self.test_obj.get_module_cache()

        self.assertIn("south", cache.keys())
        self.assertIs(type(cache["south"]), BaseModule)
        self.assertIn("South is the defacto standard for database migrations in Django", cache["south"].get_description())


    def test_clean_module_list_dependency(self):
        self.test_obj.args = type("Argh", (object,), {})
        self.test_obj.cfg["module_basedirs"] = ["."]
        self.test_obj.cfg["module_basedir"] = "../../modules"
        cache = self.test_obj.get_module_cache()
        module_list = ["django-cms"]
        clean_modules = self.test_obj.clean_module_list(module_list, cache)

        self.assertIsNot(module_list, clean_modules)
        self.assertIn("html5lib", clean_modules)

    def test_clean_module_list_duplicates(self):
        self.test_obj.args = type("Argh", (object,), {})
        self.test_obj.cfg["module_basedirs"] = ["."]
        self.test_obj.cfg["module_basedir"] = "../../modules"
        cache = self.test_obj.get_module_cache()
        module_list = ["django-cms", "html5lib"]
        clean_modules = self.test_obj.clean_module_list(module_list, cache)

        self.assertEqual(len(filter(lambda x: x == "html5lib", clean_modules)), 1)


    def test_clean_module_list_priority(self):
        self.test_obj.args = type("Argh", (object,), {})
        self.test_obj.cfg["module_basedirs"] = ["."]
        self.test_obj.cfg["module_basedir"] = "../../modules"
        cache = self.test_obj.get_module_cache()
        module_list = ["django-cms", "html5lib"]
        clean_modules = self.test_obj.clean_module_list(module_list, cache)

        self.assertEqual(clean_modules[0], "django-1.3")


    def test_inject_variables_and_functions(self):
        victim_class = type("Victim", (object,), {})

        self.test_obj.cfg["site_dir"] = "site_dir"
        self.test_obj.cfg["project_dir"] = "project_dir"
        self.test_obj.cfg["project_prefix"] = "project_prefix"
        self.test_obj.cfg["project_name"] = "project_name"
        self.test_obj.cfg["project_basedir"] = "project_basedir"

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
