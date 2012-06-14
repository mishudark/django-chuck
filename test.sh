#!/bin/sh

# run unit tests
python django_chuck/test.py
python django_chuck/commands/test.py
python django_chuck/template/notch_interactive/test.py


# test commands
chuck list_modules
chuck search_module cms
chuck show_info fabric
chuck create_project test test
