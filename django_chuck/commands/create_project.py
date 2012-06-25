import os
import sys
import shutil
from django_chuck.commands.base import BaseCommand
from django_chuck.commands import create_virtualenv, install_modules, install_virtualenv, create_database, build_snapshot, create_vagrant

class Command(BaseCommand):
    help = "Start a new project"

    def __init__(self):
        super(Command, self).__init__()

        self.opts.append(("modules", {
            "help": "modules to install",
            "nargs": "?",
        }))

        self.opts.append(("-a", {
            "help": "Comma seperated list of apps that should get installed by pip",
            "dest": "additional_apps",
            "default": None,
            "nargs": "?",
        }))


    def handle(self, args, cfg):
        super(Command, self).handle(args, cfg)

        # Project exists
        if os.path.exists(self.site_dir) and os.path.exists(self.project_dir):
            self.print_header("EXISTING PROJECT " + self.site_dir)
            answer = raw_input("Delete old project dir? <y/N>: ")

            if answer.lower() == "y" or answer.lower() == "j":
                shutil.rmtree(self.site_dir)
                os.makedirs(self.site_dir)
            else:
                print "Aborting."
                sys.exit(0)

        # Building a new project
        else:
            os.makedirs(self.site_dir)

        if self.use_vagrant:
            create_vagrant.Command().handle(args, cfg)

        create_virtualenv.Command().handle(args, cfg)
        installer = install_modules.Command()
        installer.handle(args, cfg)
        install_virtualenv.Command().handle(args, cfg)
        build_snapshot.Command().handle(args, cfg)
        create_database.Command().handle(args, cfg)


        self.print_header("SUMMARY")

        installed_modules = self.settings.get_install_modules()

        print "Created project with modules " + ", ".join(installed_modules)

        errors = []

        for module in installer.installed_modules.values():
            if module.errors:
                errors.extend(module.errors)

        if errors:
            print "\nGOT ERRORS:\n"

            for error in errors:
                print error

        if self.use_virtualenvwrapper:
            print "\nworkon " + self.site_name
        else:
            print "\nsource " + self.virtualenv_dir + "/bin/activate"

            print "cd " + self.site_dir

        print "django-admin.py createsuperuser"
