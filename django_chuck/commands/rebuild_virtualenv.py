from django_chuck.commands.base import BaseCommand
import shutil
from django_chuck.commands import create_virtualenv, install_virtualenv

class Command(BaseCommand):
    help = "Rebuild virtualenv"

    def __init__(self):
        super(Command, self).__init__()

        self.opts.append(("-a", {
            "help": "Comma seperated list of apps that should get installed by pip",
            "dest": "additional_apps",
            "default": None,
            "nargs": "?",
        }))



    def handle(self, args, cfg):
        super(Command, self).handle(args, cfg)

        self.print_header("REBUILD VIRTUALENV")

        shutil.rmtree(self.virtualenv_dir)
        create_virtualenv.Command().handle(args, cfg)
        install_virtualenv.Command().handle(args, cfg)
