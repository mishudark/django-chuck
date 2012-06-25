import sys
import functools
from random import choice
import django_chuck
from django_chuck.subsystem.database import load_fixtures, db_cleanup
from django_chuck.subsystem.shell import execute_in_project


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
    setattr(victim_class, "db_cleanup", functools.partial(db_cleanup, settings=settings))
    setattr(victim_class, "load_fixtures", functools.partial(load_fixtures, settings=settings))

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
    except ImportError, e:
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

    return engine.handle(input_file, output_file, placeholder)
