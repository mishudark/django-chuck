import sys
from django_chuck.exceptions import ShellError
from django_chuck.subsystem.shell import execute
from django_chuck.utils import print_kill_message


def checkout_source(settings):
    if settings.version_control_system.lower() == "cvs":
        if settings.branch:
            cmd ="cvs checkout -r " + settings.branch + " " + settings.checkout_url + " " + settings.checkout_destdir
        else:
            cmd ="cvs checkout " + settings.checkout_url + " " + settings.checkout_destdir
    elif settings.version_control_system.lower() == "svn":
        cmd = "svn checkout " + settings.checkout_url + " " + settings.checkout_destdir
    elif settings.version_control_system.lower() == "hg":
        if settings.branch:
            cmd = "hg clone " + settings.checkout_url + " -r " + settings.branch + " " + settings.checkout_destdir
        else:
            cmd = "hg clone " + settings.checkout_url + " " + settings.checkout_destdir
    else:
        if settings.branch:
            cmd = "git clone " + settings.checkout_url + " -b " + settings.branch + " " + settings.checkout_destdir
        else:
            cmd = "git clone " + settings.checkout_url + " " + settings.checkout_destdir

    try:
        return execute(cmd)
    except ShellError, e:
        print str(e)
        print_kill_message()
        sys.exit(1)
