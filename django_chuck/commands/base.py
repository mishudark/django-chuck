import shutil
import re
import os
import sys
from signal import signal, SIGINT, SIGILL, SIGTERM, SIGSEGV, SIGABRT, SIGQUIT
from random import choice
from django_chuck.base.modules import BaseModule
from django_chuck.exceptions import ShellError
from django_chuck import utils


# The base class for all commands

class BaseCommand(object):
    help = "The base class of all chuck commands"

    def got_killed(self, signum=2, frame=None):
        if getattr(self, "delete_project_on_failure") and self.delete_project_on_failure:
            if os.path.exists(self.site_dir):
                print "Deleting project data " + self.site_dir
                shutil.rmtree(self.site_dir)

            if os.path.exists(self.virtualenv_dir):
                print "Deleting virtualenv " + self.virtualenv_dir
                shutil.rmtree(self.virtualenv_dir)

            self.signal_handler()

        sys.exit(1)


    def signal_handler(self):
        """
        Implement this method in your command if you want to do some cleanup
        after being terminated by the user or killed by the system.
        Project and virtualenv dir will get erased automatically.
        """
        pass


    def __init__(self):
        signal(SIGINT, self.got_killed)
        signal(SIGQUIT, self.got_killed)
        signal(SIGILL, self.got_killed)
        signal(SIGABRT, self.got_killed)
        signal(SIGSEGV, self.got_killed)
        signal(SIGTERM, self.got_killed)

        # command arguments will override cfg
        self.args = None

        # config settings
        self.cfg = None

        # dont check that project prefix and name exist?
        self.no_default_checks = False

        # default options
        self.opts = [
            ("project_prefix", {
                "help": "A prefix for the project e.g. customer name. Used to distinguish between site and project dir",
                "default": None,
                "nargs": "?",
            }),

            ("project_name", {
                "help": "The name of the project",
                "default": None,
                "nargs": "?",
            }),

            ("-D", {
                "help": "debug mode",
                "dest": "debug",
                "default": False,
                "action": "store_true",
            }),

            ("-ed", {
                "help": "Your email domain",
                "dest": "email_domain",
                "default": "localhost",
                "nargs": "?",
            }),

            ("-mbs", {
                "help": "Comma separated list of dirs where chuck should look for modules",
                "dest": "module_basedir",
                "default": None,
                "nargs": "?",
            }),

            ("-pb", {
                "help": "The directory where all your projects are stored",
                "dest": "project_basedir",
                "default": None,
                "nargs": "?",
            }),

            ("-pyv", {
                "help": "Python version",
                "dest": "python_version",
                "type": float,
                "default": None,
                "nargs": "?",
            }),

            ("-s", {
                "help": "Django settings module to use after loading virtualenv",
                "dest": "django_settings",
                "default": None,
                "nargs": "?",
            }),

            ("-spb", {
                "help": "The directory on your server where all your projects are stored",
                "dest": "server_project_basedir",
                "default": None,
                "nargs": "?",
            }),

            ("-svb", {
                "help": "The directory on your server where all your virtualenvs are stored",
                "dest": "server_virtualenv_basedir",
                "default": None,
                "nargs": "?",
            }),

            ("-vb", {
                "help": "The directory where all your virtualenvs are stored",
                "dest": "virtualenv_basedir",
                "default": None,
                "nargs": "?",
            }),

            ("-vcs", {
                "help": "Version control system (git, cvs, svn or hg))",
                "dest": "version_control_system",
                "default": "git",
                "nargs": "?",
            }),

            ("-w", {
                "help": "User virtualenv wrapper to create virtualenv",
                "dest": "use_virtualenvwrapper",
                "default": False,
                "action": "store_true",
            }),
        ]


    def arg_or_cfg(self, var):
        return utils.arg_or_cfg(var, self.args, self.cfg)


    def execute(self, command, return_result=False):
        """
        Execute a command without loading virtualenv and django settings
        """
        return utils.execute(command, return_result)


    def execute_in_project(self, cmd, return_result=False):
        """
        Execute a shell command after loading virtualenv and loading django settings.
        Parameter return_result decides whether the shell command output should get
        printed out or returned.
        """
        result = ""

        try:
            result = utils.execute_in_project(cmd, self.args, self.cfg, return_result)
        except ShellError:
            self.got_killed()

        return result


    def insert_default_modules(self, module_list):
        """
        Add default modules to your module list
        Ensure that core module is the first module to install
        """
        if self.default_modules:
            for module in reversed(self.default_modules):
                if module not in module_list:
                    module_list.insert(0, module)

        if "core" in module_list:
            del module_list[module_list.index("core")]

        module_list.insert(0, "core")

        return module_list


    def get_install_modules(self):
        """
        Get list of modules to install
        Will insert default module set and resolve module aliases
        """
        try:
            install_modules = re.split("\s*,\s*", self.args.modules)
        except AttributeError:
            install_modules = []
        except TypeError:
            install_modules = []

        install_modules = self.insert_default_modules(install_modules)

        if self.cfg.get("module_aliases"):
            for (module_alias, module_list) in self.cfg.get("module_aliases").items():
                if module_alias in install_modules:
                    module_index = install_modules.index(module_alias)
                    install_modules.pop(module_index)

                    for module in reversed(module_list):
                        install_modules.insert(module_index, module)

        return install_modules

    def get_module_cache(self):
        """
        Return dict of modules with key module name and value base module
        Useful to access modules description, dependency, priority etc
        """
        # Create module dir cache
        module_cache = {}

        for module_basedir in self.module_basedirs:
            for module in os.listdir(module_basedir):
                module_dir = os.path.join(module_basedir, module)
                if os.path.isdir(module_dir) and module not in module_cache.keys():
                    module_cache[module] = BaseModule(module, self.args, self.cfg, module_dir)
                    # TODO: Ignore list for folders and filenames
                    if module_cache[module].get_post_build():
                        self.inject_variables_and_functions(module_cache[module].get_post_build())

        return module_cache


    def clean_module_list(self, module_list, module_cache):
        """
        Recursivly append dependencies to module list, remove duplicates
        and order modules by priority
        """
        errors = []

        # Add dependencies
        def get_dependencies(module_list):
            to_append = []
            for module_name in module_list:
                module = module_cache.get(module_name)
                if not module:
                    errors.append("Module %s could not be found." % module_name)
                elif module.dependencies:
                    for module_name in module.dependencies:
                        if not module_name in module_list and not module_name in to_append:
                            to_append.append(module_name)
            return to_append

        to_append = get_dependencies(module_list)
        while len(to_append) > 0:
            module_list += to_append
            to_append = get_dependencies(module_list)

        if len(errors) > 0:
            print "\n<<< ".join(errors)
            self.kill_system()

        # Check incompatibilities
        for module_name in module_list:
            module = module_cache.get(module_name)
            if module.incompatibles:
                for module_name in module.incompatibles:
                    if module_name in module_list:
                        errors.append("Module %s is not compatible with module %s" % (module.name, module_name))

        if len(errors) > 0:
            print "\n<<< ".join(errors)
            self.kill_system()

        # Order by priority
        module_list = sorted(module_list, key=lambda module: module_cache.get(module).priority)
        return module_list


    def __getattr__(self, name):
        """
        Get value either from command-line argument or config setting
        """
        return utils.get_property(name, self.args, self.cfg)


    def print_header(self, msg):
        utils.print_header(msg)

    def kill_system(self):
        """
        Your computer failed! Let it die!
        """
        utils.print_kill_message()
        self.got_killed()


    def inject_variables_and_functions(self, victim_class):
        """
        Inject variables and functions to a class
        Used for chuck_setup and chuck_module helpers
        """
        return utils.inject_variables_and_functions(victim_class, self.args, self.cfg)


    def handle(self, args, cfg):
        """
        This method includes the commands functionality
        """
        self.args = args
        self.cfg = cfg

        if not self.no_default_checks:
            if not self.project_prefix:
                raise ValueError("project_prefix is not defined")

            if not self.project_name:
                raise ValueError("project_name is not defined")
