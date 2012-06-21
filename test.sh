#!/bin/bash

# run unit tests
nosetests || exit 1


# test commands
chuck list_modules || exit 1
chuck search_module cms || exit 1
chuck show_info fabric || exit 1

chuck create_project test core || exit 1

chuck setup_project git://github.com/notch-interactive/django-chuck-testproject.git || exit 1

exit 0
