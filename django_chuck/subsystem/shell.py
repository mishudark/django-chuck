import os
import subprocess
from django_chuck.exceptions import ShellError


def get_subprocess_kwargs():
    return dict(
        shell=True,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )


def execute(command, return_result=False):
    if return_result:
        kwargs = get_subprocess_kwargs()

        if return_result:
            kwargs['stdout'] = subprocess.PIPE

        process = subprocess.Popen(command, **kwargs)
        stdout, stderr = process.communicate()

        if stderr:
            print stderr

        if process.returncode != 0:
            print return_result
            raise ShellError(command)

        return stdout
    else:
        return_code = subprocess.call(command, shell=True)

        if return_code != 0:
            raise ShellError(command)


def get_virtualenv_setup_commands(cmd, settings):
    if settings.use_virtualenvwrapper:
        commands = [
            '. virtualenvwrapper.sh',
            'workon ' + settings.site_name,
            ]
    else:
        commands = [
            '. ' + os.path.join(os.path.expanduser(settings.virtualenv_dir), "bin", "activate"),
            ]
    commands.append(cmd)
    return commands


def execute_in_project(cmd, settings, return_result=False):
    """
    Execute a shell command after loading virtualenv and loading django settings.
    Parameter return_result decides whether the shell command output should get
    printed out or returned.
    """
    commands = get_virtualenv_setup_commands(cmd, settings)
    return execute('; '.join(commands), return_result)
