import os
import re
from django_chuck.module import ChuckModule
from django_chuck import utils
from django_chuck.exceptions import ModuleError


def insert_default_modules(settings, module_list):
    """
    Add default modules to your module list
    Ensure that core module is the first module to install
    """
    if settings.default_modules:
        for module in reversed(settings.default_modules):
            if module not in module_list:
                module_list.insert(0, module)

    if "core" in module_list:
        del module_list[module_list.index("core")]

    module_list.insert(0, "core")

    return module_list


def get_install_modules(settings):
    """
    Get list of modules to install
    Will insert default module set and resolve module aliases
    """
    try:
        install_modules = re.split("\s*,\s*", settings.args.modules)
    except AttributeError:
        install_modules = []
    except TypeError:
        install_modules = []

    install_modules = insert_default_modules(settings, install_modules)

    if settings.cfg.get("module_aliases"):
        for (module_alias, module_list) in settings.cfg.get("module_aliases").items():
            if module_alias in install_modules:
                module_index = install_modules.index(module_alias)
                install_modules.pop(module_index)

                for module in reversed(module_list):
                    install_modules.insert(module_index, module)

    return install_modules


def get_module_cache(settings):
    """
    Return dict of modules with key module name and value base module
    Useful to access modules description, dependency, priority etc
    """
    # Create module dir cache
    module_cache = {}

    for module_basedir in settings.module_basedirs:
        for module in os.listdir(module_basedir):
            module_dir = os.path.join(module_basedir, module)
            if os.path.isdir(module_dir) and module not in module_cache.keys():
                module_cache[module] = ChuckModule(module, settings, module_dir)
                # TODO: Ignore list for folders and filenames
                if module_cache[module].get_post_build():
                    utils.inject_variables_and_functions(module_cache[module].get_post_build(), settings)

    return module_cache


def clean_module_list(module_list, module_cache):
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
        raise ModuleError("\n<<< ".join(errors))

    # Check incompatibilities
    for module_name in module_list:
        module = module_cache.get(module_name)
        if module.incompatibles:
            for module_name in module.incompatibles:
                if module_name in module_list:
                    errors.append("Module %s is not compatible with module %s" % (module.name, module_name))

    if len(errors) > 0:
        raise ModuleError("\n<<< ".join(errors))

    # Order by priority
    module_list = sorted(module_list, key=lambda module: module_cache.get(module).priority)
    return module_list
