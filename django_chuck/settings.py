import os
import sys
from django_chuck.subsystem.filesystem import find_chuck_module_path
from django_chuck.module.utils import get_install_modules


class Settings(object):
    def __init__(self, args=None, cfg={}):
        self.args = args
        self.cfg = cfg

    def read_config(self, conf_file=None):
        self.cfg = {
            "use_virtualenvwrapper": False,
            "site_basedir": os.path.join(os.getcwd(), "site_dir"),
            "project_basedir": os.path.join(os.getcwd(), "project_dir"),
            "virtualenv_basedir": os.path.join(os.getcwd(), "virtualenv_dir"),
            "module_basedir": find_chuck_module_path(),
        }

        if not conf_file:
            conf_file = os.path.join(os.path.expanduser('~'), "django_chuck_conf.py")

        # Read config
        if os.access(conf_file, os.R_OK):
            sys.path.insert(0, os.path.dirname(conf_file))
            conf_module = os.path.basename(conf_file).replace(".py", "")
            __import__(conf_module)

            for attr in dir(sys.modules[conf_module]):
                if not attr.startswith("_"):
                    self.cfg[attr] = getattr(sys.modules[conf_module], attr)


    def arg_or_cfg(self, var):
        """
        Get the value of an parameter or config setting
        """
        try:
            result = getattr(self.args, var)
        except AttributeError:
            result = None

        if not result:
            result = self.cfg.get(var, "")

        return result


    def __getattr__(self, name):
        result = None

        if name == "cfg":
            result = self.cfg
        elif name == "args":
            result = self.args

        elif name == "project_prefix":
            result = self.arg_or_cfg(name).replace("-", "_")

        elif name == "project_name":
            result = self.arg_or_cfg(name).replace("-", "_")

        elif name == "virtualenv_dir":
            result = os.path.join(os.path.expanduser(self.virtualenv_basedir), self.project_prefix + "-" + self.project_name)

        elif name == "site_dir":
            result = os.path.join(os.path.expanduser(self.project_basedir), self.project_prefix + "-" + self.project_name)

        elif name == "project_dir":
            result = os.path.join(self.site_dir, self.project_name)

        elif name == "delete_project_on_failure":
            result = self.arg_or_cfg(name)

        elif name == "server_project_basedir":
            result = self.arg_or_cfg(name)

            if not result:
                result = "CHANGEME"

        elif name == "server_virtualenv_basedir":
            result = self.arg_or_cfg(name)

            if not result:
                result = "CHANGEME"

        elif name == "django_settings":
            result = self.arg_or_cfg(name)

            if result and not result.startswith(self.project_name):
                result = self.project_name + "." + result
            elif not result:
                result = self.project_name + ".settings.dev"

        elif name == "requirements_file":
            result = self.arg_or_cfg(name)

            if not result:
                result = "requirements_local.txt"

        elif name == "site_name":
            result = self.project_prefix + "-" + self.project_name

        elif name == "python_version":
            result = self.arg_or_cfg(name)

            if not result:
                result = sys.version[0:3]

        elif name == "module_basedirs":
            result = self.arg_or_cfg(name)

            if result and "." in result:
                result[result.index(".")] = self.module_basedir
            elif not result:
                result = [self.module_basedir]

        else:
            result = self.arg_or_cfg(name)

        return result


    def get_install_modules(self):
        return get_install_modules(self)

    def get_placeholder(self):
        placeholder = {
            "PROJECT_PREFIX": self.project_prefix,
            "PROJECT_NAME": self.project_name,
            "SITE_NAME": self.site_name,
            "MODULE_BASEDIR": self.module_basedir,
            "PYTHON_VERSION": self.python_version,
            "PROJECT_DIR": self.project_dir,
            "PROJECT_BASEDIR": self.project_basedir,
            "VIRTUALENV_DIR": self.virtualenv_dir,
            "VIRTUALENV_BASEDIR": self.virtualenv_basedir,
            "SERVER_PROJECT_BASEDIR": self.server_project_basedir,
            "SERVER_VIRTUALENV_BASEDIR": self.server_virtualenv_basedir,
            "SITE_DIR": self.site_dir,
            "EMAIL_DOMAIN": self.email_domain,
            "MODULES": ','.join(self.modules_to_install),
        }

        return placeholder
