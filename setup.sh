#!/usr/bin/env bash

# Setup virtual environment
python -m venv env

# Install pipable packages
./env/bin/pip install -U pip
./env/bin/pip install cython
./env/bin/pip install -r requirements.txt

# Install KivEnt (not on Pypi)
git clone git@github.com:kivy/kivent.git
cd kivent
git checkout 2.2-dev
cd modules/core/
../../../env/bin/python setup.py install
cd ../../..
# rm -rf kivent


