import os
import subprocess
from django_chuck.commands.base import BaseCommand
from django_chuck.subsystem.vagrant import vagrant_start_box, vagrant_ssh
from django_chuck.module import ChuckModule


class Command(BaseCommand):
    help = "Create a vagrant image and configure it to serve chucks project"

    def __init__(self):
        super(Command, self).__init__()

        self.opts.append(("-Vb", {
            "help": "vagrant box to use",
            "dest": "vagrant_box",
            "default": "http://files.vagrantup.com/lucid32.box",
            "nargs": "?",
        }))

        self.opts.append(("-Vc", {
            "help": "commands to execute after image is set up",
            "dest": "vagrant_commands",
            "default": "",
            "nargs": "?",
        }))

        self.opts.append(("-Vd", {
            "help": "where shall we create the new box?",
            "dest": "vagrant_basedir",
            "nargs": "?",
        }))


    def signal_handler(self):
        super(Command, self).signal_handler()

        cmd = "cd %s; vagrant destroy" % (self.get_box_path(),)
        subprocess.call(cmd, shell=True)


    def handle(self, args, cfg):
        super(Command, self).handle(args, cfg)

        module = ChuckModule("vagrant", self.settings)
        module.install(exec_post_build=True)

        vagrant_start_box(self.settings)

        if self.vagrant_commands:
            vagrant_ssh(self.settings)
