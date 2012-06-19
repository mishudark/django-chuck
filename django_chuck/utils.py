import os
import sys
import functools
import subprocess
from random import choice
import django_chuck
from django_chuck.exceptions import ShellError


def get_files(dir):
    """
    Recursivly read a directory and return list of all files
    """
    files = []

    for (path, subdirs, new_files) in os.walk(dir):
        for new_file in new_files:
            files.append(os.path.join(path, new_file))

    return files


def write_to_file(out_file, data):
    """
    copy data to out_file
    """
    if os.access(out_file, os.W_OK):
        out = open(out_file, "wb")
    else:
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))

        out = open(out_file, "wb")

    out.write(data)
    out.close()


def append_to_file(out_file, data):
    """
    append data to out_file
    """
    if os.access(out_file, os.W_OK):
        out = open(out_file, "ab")
    else:
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))

        out = open(out_file, "ab")

    out.write(data)
    out.close()



def find_chuck_module_path():
    """
    Return path to chuck modules
    """
    return os.path.join(sys.prefix, "share", "django_chuck", "modules")


def find_chuck_command_path():
    """
    Search for path to chuck commands in sys.path
    """
    module_path = None

    for path in sys.path:
        full_path = os.path.join(path, "django_chuck", "commands")

        if os.path.exists(full_path):
            module_path = full_path
            break

    return module_path


def find_commands():
    """
    Find all django chuck commands and create a list of module names
    """
    commands = []
    command_path = find_chuck_command_path()

    if command_path:
        for f in os.listdir(command_path):
            if not f.startswith("_") and f.endswith(".py") and \
               not f == "base.py" and not f == "test.py":
                commands.append(f[:-3])

    return commands


def autoload_commands(subparsers, settings, command_list):
    """
    Load all commands in command_list and create argument parsers
    """
    for cmd_name in command_list:
        module_name = "django_chuck.commands." + cmd_name
        __import__(module_name)

        if getattr(sys.modules[module_name], "Command"):
            cmd = sys.modules[module_name].Command()
            cmd_parser = subparsers.add_parser(cmd_name, help=cmd.help)

            try:
                for arg in cmd.opts:
                    cmd_parser.add_argument(arg[0], **arg[1])
            except TypeError, e:
                print "Broken argument configuration in command " + cmd_name + " argument " + str(arg)
                print str(e)
                sys.exit(0)

            handle_cmd = functools.partial(cmd.handle, cfg=settings.cfg)
            cmd_parser.set_defaults(func=handle_cmd)

    return True




def get_subprocess_kwargs():
    return dict(
        shell=True,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )


def execute(command, return_result=False):
    if return_result:
        kwargs = get_subprocess_kwargs()

        if return_result:
            kwargs['stdout'] = subprocess.PIPE

        process = subprocess.Popen(command, **kwargs)
        stdout, stderr = process.communicate()

        if stderr:
            print stderr

        if process.returncode != 0:
            print return_result
            raise ShellError("Command " + command)

        return stdout
    else:
        return_code = subprocess.call(command, shell=True)

        if return_code != 0:
            raise ShellError("Command " + command)


def get_virtualenv_setup_commands(cmd, settings):
    if settings.use_virtualenvwrapper:
        commands = [
            '. virtualenvwrapper.sh',
            'workon ' + settings.site_name,
            ]
    else:
        commands = [
            '. ' + os.path.join(os.path.expanduser(settings.virtualenv_dir), "bin", "activate"),
            ]
    commands.append(cmd)
    return commands


def execute_in_project(cmd, settings, return_result=False):
    """
    Execute a shell command after loading virtualenv and loading django settings.
    Parameter return_result decides whether the shell command output should get
    printed out or returned.
    """
    commands = get_virtualenv_setup_commands(cmd, settings)
    return execute('; '.join(commands), return_result)




def db_cleanup():
    """
    Sync and migrate, delete content types and load fixtures afterwards
    This is for example useful for complete django-cms migrations
    NOTE: This command will not erase your old database!
    """
    # os.chdir(self.site_dir)
    # sys.path.append(self.site_dir)

    # os.environ["DJANGO_SETTINGS_MODULE"] = self.django_settings
    # # __import__(self.django_settings)
    # # #settings.configure(default_settings=self.django_settings)

    # #from django.utils.importlib import import_module
    # #import_module(self.django_settings)

    # from django.db import connection, transaction
    # from django.conf import settings

    # cursor = connection.cursor()

    # if settings.DATABASE_ENGINE.startswith("postgresql"):
    #     cursor.execute("truncate django_content_type cascade;")
    # else:
    #     cursor.execute("DELETE FROM auth_permission;")
    #     cursor.execute("DELETE FROM django_admin_log;")
    #     cursor.execute("DELETE FROM auth_user;")
    #     cursor.execute("DELETE FROM auth_group_permissions;")
    #     cursor.execute("DELETE FROM auth_user_user_permissions;")
    #     cursor.execute("DELETE FROM django_content_type;")
    #     cursor.execute("DELETE FROM django_site;")
    #     cursor.execute("DELETE FROM south_migrationhistory;")

    # transaction.commit_unless_managed()
    # sys.path.pop()

    cmd = """DELETE FROM auth_permission;
    DELETE FROM django_admin_log;
    DELETE FROM auth_user;
    DELETE FROM auth_group_permissions;
    DELETE FROM auth_user_user_permissions;
    DELETE FROM django_content_type;
    DELETE FROM django_site;
    DELETE FROM south_migrationhistory;"""

    execute_in_project("echo '" + cmd + "' | django-admin.py dbshell")


def load_fixtures(fixture_file):
    """
    Load a fixtures file
    """
    execute_in_project("django-admin.py loaddata " + fixture_file)


def inject_variables_and_functions(victim_class, settings):
    """
    Inject variables and functions to a class
    Used for chuck_setup and chuck_module helpers
    """
    # inject variables
    setattr(victim_class, "virtualenv_dir", settings.virtualenv_dir)
    setattr(victim_class, "site_dir", settings.site_dir)
    setattr(victim_class, "project_dir", settings.project_dir)
    setattr(victim_class, "project_name", settings.project_name)
    setattr(victim_class, "site_name", settings.site_name)

    # inject functions
    setattr(victim_class, "execute_in_project", functools.partial(execute_in_project, settings=settings))
    setattr(victim_class, "db_cleanup", db_cleanup)
    setattr(victim_class, "load_fixtures", load_fixtures)

    return victim_class


def print_header(msg):
    """
    Print a header message
    """
    print "\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
    print "[PHASE]: " + msg
    print "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"


def print_kill_message():
    """
    Your computer failed! Let it die!
    """
    msgs = [
        "Your system gave an Chuck incompatible answer!",
        "The system failed to obey Chuck! Terminate!",
        "Chuck stumbled over his feet and the world fell apart.",
        "Your computer lied to Chuck. Now it tastes a roundhouse-kick!",
        "That was a serious failure. May god forgive Chuck doesnt!",
        "Death to the system for being so faulty!",
    ]

    print "\n<<< " + choice(msgs)


def get_template_engine(site_dir, project_dir, engine_module=None):
    """
    Get template engine instance
    """
    default_engine = "django_chuck.template.notch_interactive.engine"

    if not engine_module:
        engine_module = default_engine

    try:
        __import__(engine_module)
    except Exception, e:
        print "\n<<< Cannot import template engine " + engine_module
        print e
        sys.exit(0)

    if getattr(sys.modules[engine_module], "TemplateEngine"):
        engine = sys.modules[engine_module].TemplateEngine(site_dir, project_dir)
    else:
        print "<<< Template engine " + engine_module + " must implement class TemplateEngine"
        sys.exit(0)

    return engine


def compile_template(input_file, output_file, placeholder, site_dir, project_dir, engine_obj=None, debug=False):
    """
    Load the template engine and let it deal with the output_file
    Parameter: name of template file, dictionary of placeholder name / value pairs, name of template engine module
    """
    result = True

    if output_file.endswith(".pyc") or \
       output_file.endswith(".mo"):
        return None

    if engine_obj and issubclass(engine_obj.__class__, django_chuck.template.base.BaseEngine):
        engine = engine_obj
    else:
        engine = get_template_engine(site_dir, project_dir)

    try:
        engine.handle(input_file, output_file, placeholder)
    except django_chuck.exceptions.TemplateError, e:
        print "\n<<< TEMPLATE ERROR in file " + input_file + "\n"
        print str(e) + "\n"
        result = False

    return result
