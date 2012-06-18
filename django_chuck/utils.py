import os
import sys
import functools
import django_chuck


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


def autoload_commands(subparsers, cfg, command_list):
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


            handle_cmd = functools.partial(cmd.handle, cfg=cfg)
            cmd_parser.set_defaults(func=handle_cmd)

    return True


def arg_or_cfg(var, args, cfg):
    """
    Get the value of an parameter or config setting
    """
    try:
        result = getattr(args, var)
    except AttributeError:
        result = None

    if not result:
        result = cfg.get(var, "")

    return result


def get_property(name, args, cfg):
    result = None

    if name == "cfg":
        result = cfg
    elif name == "args":
        result = args

    elif name == "project_prefix":
        result = arg_or_cfg(name, args, cfg).replace("-", "_")

    elif name == "project_name":
        result = arg_or_cfg(name, args, cfg).replace("-", "_")

    elif name == "virtualenv_dir":
        result = os.path.join(os.path.expanduser(get_property("virtualenv_basedir", args, cfg)), get_property("project_prefix", args, cfg) + "-" + get_property("project_name", args, cfg))

    elif name == "site_dir":
        result = os.path.join(os.path.expanduser(get_property("project_basedir", args, cfg)), get_property("project_prefix", args, cfg) + "-" + get_property("project_name", args, cfg))

    elif name == "project_dir":
        result = os.path.join(get_property("site_dir", args, cfg), get_property("project_name", args, cfg))

    elif name == "delete_project_on_failure":
        result = arg_or_cfg(name, args, cfg)

    elif name == "server_project_basedir":
        result = arg_or_cfg(name, args, cfg)

        if not result:
            result = "CHANGEME"

    elif name == "server_virtualenv_basedir":
        result = arg_or_cfg(name, args, cfg)

        if not result:
            result = "CHANGEME"

    elif name == "django_settings":
        result = arg_or_cfg(name, args, cfg)

        if result and not result.startswith(get_property("project_name", args, cfg)):
            result = get_property("project_name", args, cfg) + "." + result
        elif not result:
            result = get_property("project_name", args, cfg) + ".settings.dev"

    elif name == "requirements_file":
        result = arg_or_cfg(name, args, cfg)

        if not result:
            result = "requirements_local.txt"

    elif name == "site_name":
        result = get_property("project_prefix", args, cfg) + "-" + get_property("project_name", args, cfg)

    elif name == "python_version":
        result = arg_or_cfg(name, args, cfg)

        if not result:
            result = sys.version[0:3]

    elif name == "module_basedirs":
        result = arg_or_cfg(name, args, cfg)

        if result and "." in result:
            result[result.index(".")] = get_property("module_basedir", args, cfg)
        elif not result:
            result = [get_property("module_basedir", args, cfg)]

    else:
        result = arg_or_cfg(name, args, cfg)

    return result


def get_placeholder(args, cfg):
    placeholder = {
        "PROJECT_PREFIX": get_property("project_prefix", args, cfg),
        "PROJECT_NAME": get_property("project_name", args, cfg),
        "SITE_NAME": get_property("site_name", args, cfg),
        "MODULE_BASEDIR": get_property("module_basedir", args, cfg),
        "PYTHON_VERSION": get_property("python_version", args, cfg),
        "PROJECT_BASEDIR": get_property("project_basedir", args, cfg),
        "VIRTUALENV_BASEDIR": get_property("virtualenv_basedir", args, cfg),
        "SERVER_PROJECT_BASEDIR": get_property("server_project_basedir", args, cfg),
        "SERVER_VIRTUALENV_BASEDIR": get_property("server_virtualenv_basedir", args, cfg),
        "EMAIL_DOMAIN": get_property("email_domain", args, cfg),
        "MODULES": ','.join(get_property("modules_to_install)", args, cfg)),
    }

    return placeholder


def inject_variables_and_functions(victim_class, args, cfg):
    """
    Inject variables and functions to a class
    Used for chuck_setup and chuck_module helpers
    """
    # inject variables
    setattr(victim_class, "virtualenv_dir", get_property("virtualenv_dir", args, cfg))
    setattr(victim_class, "site_dir", get_property("site_dir", args, cfg))
    setattr(victim_class, "project_dir", get_property("project_dir", args, cfg))
    setattr(victim_class, "project_name", get_property("project_name", args, cfg))
    setattr(victim_class, "site_name", get_property("site_name", args, cfg))

    # inject functions
    setattr(victim_class, "execute_in_project", get_property("execute_in_project", args, cfg))
    setattr(victim_class, "db_cleanup", get_property("db_cleanup", args, cfg))
    setattr(victim_class, "load_fixtures", get_property("load_fixtures", args, cfg))

    return victim_class


def print_header(msg):
    """
    Print a header message
    """
    print "\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
    print "[PHASE]: " + msg
    print "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"


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

    if issubclass(engine_obj.__class__, django_chuck.template.base.BaseEngine):
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
