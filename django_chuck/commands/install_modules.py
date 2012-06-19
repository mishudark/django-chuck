from django_chuck.commands.base import BaseCommand
import os
import sys
import shutil
from django_chuck.utils import append_to_file, get_files, get_template_engine, compile_template
from random import choice

class Command(BaseCommand):
    help = "Create all modules"

    # Which modules shall be installed
    modules_to_install = []

    # Remember which module were already installed
    installed_modules = []

    # Remember where we can find which module
    module_cache = {}

    # Post build actions
    post_build_actions = []

    def __init__(self):
        super(Command, self).__init__()

        self.opts.append(("modules", {
            "help": "Comma seperated list of module names (can include pip modules)",
            "default": "core",
            "nargs": "?",
        }))

    def install_module(self, module_name):
        module = self.module_cache.get(module_name, None)

        if module.name not in self.installed_modules:
            # Module has post build action? Remember it
            if module.get_post_build():
                self.inject_variables_and_functions(module.meta_data)
                setattr(module.get_post_build(), "installed_modules", self.installed_modules)
                self.post_build_actions.append((module.name, module.get_post_build()))

            module.install()
            self.installed_modules.append(module.name)


    def handle(self, args, cfg):
        super(Command, self).handle(args, cfg)

        self.installed_modules = []

        # Get module cache
        self.module_cache = self.get_module_cache()

        # Modules to install
        self.modules_to_install = self.get_install_modules()

        # The template engine that is used to compile the project files
        template_engine = get_template_engine(self.site_dir, self.project_dir, cfg.get("template_engine"))

        # Clean module list
        self.modules_to_install = self.clean_module_list(self.modules_to_install, self.module_cache)

        # Install each module
        for module in self.modules_to_install:
            self.install_module(module)

        not_installed_modules = [m for m in self.modules_to_install if not m in self.installed_modules]

        if not_installed_modules:
            print "\n<<< The following modules cannot be found " + ",".join(not_installed_modules)
            self.kill_system()

        # we are using notch interactive template engine
        # so we want to remove all chuck keywords after successful build
        if (self.template_engine == "django_chuck.template.notch_interactive.engine" or not self.template_engine) and\
           not self.debug:
            for f in get_files(self.site_dir):
                template_engine.remove_keywords(f)


        # execute post build actions
        if self.post_build_actions:
            self.print_header("EXECUTING POST BUILD ACTIONS")

            for action in self.post_build_actions:
                print ">>> " + action[0]
                try:
                    action[1]()
                    print "\n"
                except Exception, e:
                    print str(e)
                    self.kill_system()
