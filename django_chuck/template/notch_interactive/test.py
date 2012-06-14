import os
import re
import shutil
import unittest
from engine import TemplateEngine
from django_chuck.exceptions import TemplateError


class TemplateEngineTest(unittest.TestCase):
    def setUp(self):
        self.engine = TemplateEngine("django_chuck/template/notch_interactive/test", "django_chuck/template/notch_interactive//test/project_dir")

        if not os.path.exists("django_chuck/template/notch_interactive//test/project_dir"):
            os.makedirs("django_chuck/template/notch_interactive//test/project_dir")

    def test_get_block_content(self):
        with open("django_chuck/template/notch_interactive/test/templates/common.py", "r") as f:
            content = f.read()
            block_content = self.engine.get_block_content(content, "MIDDLEWARE_CLASSES")
            self.assertFalse("#!chuck" in block_content)

            block_content = self.engine.get_block_content(content, "SETTINGS")
            self.assertEqual(block_content, " ")

    #
    # TEST BASIC KEYWORDS
    #

    def test_renders(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/base.html", "django_chuck/template/notch_interactive/test/project_dir/base.html")
        self.engine.handle("django_chuck/template/notch_interactive/test/templates/replace.html", "django_chuck/template/notch_interactive/test/project_dir/replace.html", {})

        with open("django_chuck/template/notch_interactive/test/project_dir/base.html") as f:
            content = f.read()
            self.assertTrue("<html>" in content)
            self.assertTrue("#!chuck_renders content" in content)


    def test_render_multiple_blocks(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/base.html", "django_chuck/template/notch_interactive/test/project_dir/base.html")
        self.engine.handle("django_chuck/template/notch_interactive/test/templates/replace_three_blocks.html", "django_chuck/template/notch_interactive/test/project_dir/replace_three_blocks.html", {})

        with open("django_chuck/template/notch_interactive/test/project_dir/base.html") as f:
            content = f.read()
            self.assertTrue("<html>" in content)
            self.assertTrue("#!chuck_renders content" in content)
            self.assertTrue("lets start" in content)
            self.assertTrue("MOOOOOH" in content)
            self.assertTrue("go home" in content)


    def test_appends(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/base.html", "django_chuck/template/notch_interactive/test/project_dir/base.html")
        self.engine.handle("django_chuck/template/notch_interactive/test/templates/append.html", "django_chuck/template/notch_interactive/test/project_dir/append.html", {})

        with open("django_chuck/template/notch_interactive/test/project_dir/base.html") as f:
            content = f.read()
            self.assertTrue(re.search(r"One must have chaos in oneself to give birth to a dancing star.+The big MOOOOOH has pwned you", content, re.MULTILINE|re.DOTALL), content)


    def test_prepends(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/base.html", "django_chuck/template/notch_interactive/test/project_dir/base.html")
        self.engine.handle("django_chuck/template/notch_interactive/test/templates/prepend.html", "django_chuck/template/notch_interactive/test/project_dir/prepend.html", {})

        with open("django_chuck/template/notch_interactive/test/project_dir/base.html") as f:
            content = f.read()
            self.assertTrue(re.search(r"The big MOOOOOH has pwned you.+One must have chaos in oneself to give birth to a dancing star", content, re.MULTILINE|re.DOTALL), content)


    def test_extends_if_exists(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/base.html", "django_chuck/template/notch_interactive/test/project_dir/base.html")
        self.engine.handle("django_chuck/template/notch_interactive/test/templates/extends_if_exists.html", "django_chuck/template/notch_interactive/test/project_dir/extends_if_exists.html", {})

        with open("django_chuck/template/notch_interactive/test/project_dir/base.html") as f:
            content = f.read()
            self.assertTrue(re.search(r"One must have chaos in oneself to give birth to a dancing star.+The big MOOOOOH has pwned you", content, re.MULTILINE|re.DOTALL), content)


    def test_placeholder(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/base.html", "django_chuck/template/notch_interactive/test/project_dir/base.html")
        self.engine.handle("django_chuck/template/notch_interactive/test/templates/placeholder.html", "django_chuck/template/notch_interactive/test/project_dir/placeholder.html", {"SOMETHING": "cool things"})

        with open("django_chuck/template/notch_interactive/test/project_dir/base.html") as f:
            content = f.read()
            self.assertTrue("cool things" in content)


    def test_placeholder_without_extend(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/placeholder_without_extend.html", "django_chuck/template/notch_interactive/test/project_dir/placeholder_without_extend.html")
        self.engine.handle("django_chuck/template/notch_interactive/test/templates/placeholder_without_extend.html", "django_chuck/template/notch_interactive/test/project_dir/placeholder_without_extend.html", {"SOMETHING": "cool things"})

        with open("django_chuck/template/notch_interactive/test/project_dir/placeholder_without_extend.html") as f:
            content = f.read()
            self.assertTrue("cool things" in content)


    def test_remove_keywords(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/remove_keywords.html", "django_chuck/template/notch_interactive/test/project_dir/remove_keywords.html")
        self.engine.handle("django_chuck/template/notch_interactive/test/project_dir/remove_keywords.html", "test/project_dir/remove_keywords.html", {})
        self.engine.remove_keywords("django_chuck/template/notch_interactive/test/project_dir/remove_keywords.html")

        with open("django_chuck/template/notch_interactive/test/project_dir/remove_keywords.html") as f:
            content = f.read()
            self.assertFalse("#!chuck" in content, content)
            self.assertTrue("chaos" in content, content)



    def test_complex_example(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/common.py", "django_chuck/template/notch_interactive/test/project_dir/common.py")

        self.engine.handle("django_chuck/template/notch_interactive/test/templates/extends_common.py", "django_chuck/template/notch_interactive/test/project_dir/extends_common.py", {"PROJECT_NAME": "test"})
        self.engine.remove_keywords("django_chuck/template/notch_interactive/test/project_dir/common.py")

        with open("django_chuck/template/notch_interactive/test/project_dir/common.py") as f:
            content = f.read()
            self.assertTrue("# -*- coding" in content.splitlines()[0])  # right order
            self.assertTrue("CMS_TEMPLATES" in content)                 # appends
            self.assertTrue("ROOT_URLCONF = 'test.urls'" in content)    # placeholder
            self.assertFalse("#!chuck" in content, content)         # removed keywords


    #
    # ADVANCED FEATURES
    #

    def test_extends_two_files(self):
        shutil.copy("django_chuck/template/notch_interactive/test/templates/base.html", "django_chuck/template/notch_interactive/test/project_dir/base.html")
        shutil.copy("django_chuck/template/notch_interactive/test/templates/base2.html", "django_chuck/template/notch_interactive/test/project_dir/base2.html")

        self.engine.handle("django_chuck/template/notch_interactive/test/templates/extend_two_files.html", "django_chuck/template/notch_interactive/test/project_dir/extend_two_files.html", {})

        with open("django_chuck/template/notch_interactive/test/project_dir/base.html") as f:
            content = f.read()
            self.assertTrue("big MOOOOOH" in content)
            self.assertTrue("#!chuck_renders content" in content)

        with open("django_chuck/template/notch_interactive/test/project_dir/base2.html") as f:
            content = f.read()
            self.assertTrue("Balle was here" in content)
            self.assertTrue("#!chuck_renders content" in content)



    #
    # ERRORS
    #
    def test_keyword_not_found(self):
        try:
            self.engine.handle("django_chuck/template/notch_interactive/test/templates/broken_keyword.html", "django_chuck/template/notch_interactive/test/project_dir/broken_keyword.html", {})
            test_failed = True
        except TemplateError:
            test_failed = False

        self.assertFalse(test_failed)

    def test_syntax_error(self):
        try:
            self.engine.handle("django_chuck/template/notch_interactive/test/templates/broken_syntax.html", "django_chuck/template/notch_interactive/test/project_dir/broken_syntax.html", {})
            test_failed = True
        except TemplateError:
            test_failed = False

        self.assertFalse(test_failed)


    def test_non_existent_block_name(self):
        try:
            self.engine.handle("django_chuck/template/notch_interactive/test/templates/broken_block_name.html", "django_chuck/template/notch_interactive/test/project_dir/brocken_block_name.html", {})
            test_failed = True
        except TemplateError:
            test_failed = False

        self.assertFalse(test_failed)


    def test_non_existent_base_file(self):
        try:
            self.engine.handle("django_chuck/template/notch_interactive/test/templates/broken_base_file.html", "django_chuck/template/notch_interactive/test/project_dir/broken_base_file.html", {})
            test_failed = True
        except TemplateError:
            test_failed = False

        self.assertFalse(test_failed)

    def test_non_existent_base_file_with_if_exists(self):
        self.engine.handle("django_chuck/template/notch_interactive/test/templates/broken_base_file_with_if_exists.html", "django_chuck/template/notch_interactive/test/project_dir/broken_base_file_with_if_exists.html", {})


if __name__ == '__main__':
    unittest.main()
