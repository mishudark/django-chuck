import os
import shutil
import subprocess
from django_chuck.commands.base import BaseCommand
from django_chuck.base.modules import BaseModule


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


    def get_box_path(self):
        return os.path.join(os.path.expanduser(self.site_dir), "vagrant")


    def signal_handler(self):
        super(Command, self).signal_handler()

        cmd = "cd %s; vagrant destroy" % (self.get_box_path(),)
        subprocess.call(cmd, shell=True)


    def handle(self, args, cfg):
        super(Command, self).handle(args, cfg)

        module = BaseModule("vagrant", args, cfg)
        module.install(exec_post_build=True)

        box_path = self.get_box_path()

        cmd = "cd %s; vagrant box add %s_box %s; vagrant up" % (box_path, self.project_name, self.vagrant_box)
        subprocess.call(cmd, shell=True)

        if self.vagrant_commands:
            cmd = "cd %s; vagrant ssh -c '%s'" % (box_path, self.vagrant_commands)
            subprocess.call(cmd, shell=True)
