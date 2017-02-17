#!/usr/bin/env bash
set -e  # quit on error
# Setup and activate virtual environment
python -m venv env
. env/bin/activate


# Download KivEnt from github (not on Pypi)
git clone git@github.com:kivy/kivent.git --branch 2.2-dev

# Install packages
# NOTE: This method is used to specify exactly the install order because
# kivy/kivent do not properly specify their dependencies
xargs -L 1 pip install < requirements.txt
