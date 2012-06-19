import os
import subprocess


def get_box_path(settings):
    return os.path.join(os.path.expanduser(settings.site_dir), "vagrant")


def vagrant_start_box(settings):
    cmd = "cd %s; vagrant box xadd %s_box %s; vagrant up" % (get_box_path(settings), settings.project_name, settings.vagrant_box)
    subprocess.call(cmd, shell=True)


def vagrant_stop_box(settings):
    cmd = "cd %s; vagrant box xadd %s_box %s; vagrant halt" % (get_box_path(settings), settings.project_name, settings.vagrant_box)
    subprocess.call(cmd, shell=True)


def vagrant_ssh(settings, command=None):
    cmd = "cd %s; vagrant ssh -c " % (get_box_path(settings),)

    if command:
        cmd += "'" + command + "'"
    else:
        cmd += "'" + settings.vagrant_commands + "'"

    subprocess.call(cmd, shell=True)
