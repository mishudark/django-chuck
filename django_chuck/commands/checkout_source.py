import os
import shutil
import tempfile
from django_chuck.commands.base import BaseCommand
from django_chuck.subsystem.version_control_system import checkout_source


class Command(BaseCommand):
    help = "Checkout the source code"

    def __init__(self):
        super(Command, self).__init__()

        self.no_default_checks = True

        self.opts.append((
            "checkout_url", {
                "help": "repository url",
            }))

        self.opts.append((
            "-cd", {
                "help": "destination directory",
                "dest": "checkout_destdir",
                "default": "",
                "nargs": "?"
            }),
        )

        self.opts.append((
            "-b", {
                "help": "branch to checkout / clone",
                "dest": "branch",
                "default": "",
                "nargs": "?"
            }),
        )


    def signal_handler(self):
        if os.path.exists(self.checkout_destdir):
            print "Deleting checkout directory " + self.checkout_destdir
            shutil.rmtree(self.checkout_destdir)


    def handle(self, args, cfg):
        super(Command, self).handle(args, cfg)

        if not self.checkout_url:
            raise ValueError("checkout_url is not defined")

        if not self.settings.checkout_destdir:
            self.settings.checkout_destdir = tempfile.mktemp()

        self.print_header("CHECKOUT SOURCE")

        if os.path.exists(self.settings.checkout_destdir):
            answer = raw_input("Checkout dir exists. Use old source? <Y/n>: ")

            if answer.lower() == "n":
                shutil.rmtree(self.settings.checkout_destdir)
            else:
                return

        if checkout_source(self.settings) > 0:
            self.kill_system()
