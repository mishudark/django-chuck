from django_chuck.subsystem.shell import execute_in_project


def db_cleanup(settings):
    """
    Sync and migrate, delete content types and load fixtures afterwards
    This is for example useful for complete django-cms migrations
    NOTE: This command will not erase your old database!
    """
    # os.chdir(self.site_dir)
    # sys.path.append(self.site_dir)

    # os.environ["DJANGO_SETTINGS_MODULE"] = self.django_settings
    # # __import__(self.django_settings)
    # # #settings.configure(default_settings=self.django_settings)

    # #from django.utils.importlib import import_module
    # #import_module(self.django_settings)

    # from django.db import connection, transaction
    # from django.conf import settings

    # cursor = connection.cursor()

    # if settings.DATABASE_ENGINE.startswith("postgresql"):
    #     cursor.execute("truncate django_content_type cascade;")
    # else:
    #     cursor.execute("DELETE FROM auth_permission;")
    #     cursor.execute("DELETE FROM django_admin_log;")
    #     cursor.execute("DELETE FROM auth_user;")
    #     cursor.execute("DELETE FROM auth_group_permissions;")
    #     cursor.execute("DELETE FROM auth_user_user_permissions;")
    #     cursor.execute("DELETE FROM django_content_type;")
    #     cursor.execute("DELETE FROM django_site;")
    #     cursor.execute("DELETE FROM south_migrationhistory;")

    # transaction.commit_unless_managed()
    # sys.path.pop()

    cmd = """DELETE FROM auth_permission;
    DELETE FROM django_admin_log;
    DELETE FROM auth_user;
    DELETE FROM auth_group_permissions;
    DELETE FROM auth_user_user_permissions;
    DELETE FROM django_content_type;
    DELETE FROM django_site;
    DELETE FROM south_migrationhistory;"""

    execute_in_project("echo '" + cmd + "' | django-admin.py dbshell", settings)


def load_fixtures(fixture_file, settings):
    """
    Load a fixtures file
    """
    execute_in_project("django-admin.py loaddata " + fixture_file, settings)
