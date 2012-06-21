import unittest
from django_chuck.settings import Settings

class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_read_config(self):
        self.settings.read_config("django_chuck/tests/test_conf.py")

        self.assertEqual(self.settings.cfg["requirements_file"], "requirements_local.txt")
        self.assertFalse(self.settings.cfg["debug"])


    def test_arg_or_cfg(self):
        self.settings.arg = {}
        self.settings.cfg["project_name"] = "balle was here"
        self.assertEqual(self.settings.arg_or_cfg("project_name"), "balle was here")


    def test_getattr(self):
        self.settings.arg = {}
        self.settings.cfg["project_name"] = "balle was here"
        self.assertEqual(self.settings.project_name, "balle was here")


    def test_get_placeholder(self):
        self.settings.arg = {}
        self.settings.cfg["project_name"] = "balle was here"
        placeholder = self.settings.get_placeholder()

        self.assertEqual(placeholder["PROJECT_NAME"], "balle was here")
