import shutil
import re
import os
import sys
from signal import signal, SIGINT, SIGILL, SIGTERM, SIGSEGV, SIGABRT, SIGQUIT
from random import choice
from django_chuck.base.modules import BaseModule
from django_chuck.exceptions import ShellError
from django_chuck.settings import Settings
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

        self.settings = None

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
            result = utils.execute_in_project(cmd, self.settings, return_result)
        except ShellError:
            self.got_killed()

        return result




    def __getattr__(self, name):
        """
        Get value either from command-line argument or config setting
        """
        return getattr(self.settings, name)


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
        return utils.inject_variables_and_functions(victim_class, self.settings)


    def handle(self, args, cfg):
        """
        This method includes the commands functionality
        """
        self.settings = Settings(args=args, cfg=cfg)

        if not self.no_default_checks:
            if not self.project_prefix:
                raise ValueError("project_prefix is not defined")

            if not self.project_name:
                raise ValueError("project_name is not defined")
