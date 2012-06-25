import os
import sys


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
    if os.path.exists(os.path.join(os.getcwd(), "modules")):
        return os.path.join(os.getcwd(), "modules")

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
