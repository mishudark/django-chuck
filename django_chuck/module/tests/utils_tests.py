import unittest
from django_chuck.module.utils import insert_default_modules, get_module_cache, clean_module_list, get_install_modules
from django_chuck.settings import Settings

class ModuleUtilsTest(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(cfg={})

    def test_insert_default_modules(self):
        self.settings.cfg["default_modules"] = ["tick", "trick", "track"]
        self.assertEqual(insert_default_modules(self.settings, ["donald"]), ["core", "tick", "trick", "track", "donald"])


    def test_get_install_modules(self):
        self.settings.args = type("Argh", (object,), {"modules": "simpsons, futurama"})
        self.settings.cfg["default_modules"] = ["tick", "trick", "track"]
        self.settings.cfg["module_aliases"] = {"simpsons": ["homer", "marge", "bart", "lisa", "maggie"]}
        self.assertEqual(get_install_modules(self.settings), ["core", "tick", "trick", "track", "homer", "marge", "bart", "lisa", "maggie", "futurama"])


    def test_get_module_cache(self):
        from django_chuck.module import ChuckModule

        self.settings.args = type("Argh", (object,), {})
        self.settings.cfg["module_basedirs"] = ["."]
        self.settings.cfg["module_basedir"] = "modules"

        cache = get_module_cache(self.settings)

        self.assertTrue("south" in cache.keys())
        self.assertEqual(cache["south"].__class__, ChuckModule)
        self.assertTrue("South is the defacto standard for database migrations in Django" in cache["south"].get_description())


    def test_clean_module_list_dependency(self):
        self.settings.args = type("Argh", (object,), {})
        self.settings.cfg["module_basedirs"] = ["."]
        self.settings.cfg["module_basedir"] = "modules"
        cache = get_module_cache(self.settings)
        module_list = ["django-cms"]
        clean_modules = clean_module_list(module_list, cache)

        self.assertTrue("html5lib" in clean_modules)

    def test_clean_module_list_duplicates(self):
        self.settings.args = type("Argh", (object,), {})
        self.settings.cfg["module_basedirs"] = ["."]
        self.settings.cfg["module_basedir"] = "modules"
        cache = get_module_cache(self.settings)
        module_list = ["django-cms", "html5lib"]
        clean_modules = clean_module_list(module_list, cache)

        self.assertEqual(len(filter(lambda x: x == "html5lib", clean_modules)), 1)


    def test_clean_module_list_priority(self):
        self.settings.args = type("Argh", (object,), {})
        self.settings.cfg["module_basedirs"] = ["."]
        self.settings.cfg["module_basedir"] = "modules"
        cache = get_module_cache(self.settings)
        module_list = ["django-cms", "html5lib"]
        clean_modules = clean_module_list(module_list, cache)

        self.assertEqual(clean_modules[0], "django-1.3")
