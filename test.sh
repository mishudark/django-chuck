#!/bin/sh

# run unit tests
cd django_chuck
python test.py

cd commands
python test.py

cd ../template/notch_interactive
python test.py


# test commands
chuck list_modules
chuck search_module cms
chuck show_info fabric
chuck create_project test test
