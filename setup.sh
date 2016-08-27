#!/usr/bin/env bash

# Setup virtual environment
python -m venv env

# Install pipable packages
./env/bin/pip install -U pip
./env/bin/pip install cython
./env/bin/pip install -r requirements.txt

# Install KivEnt (not on Pypi)
wget https://github.com/kivy/KivEnt/tarball/master -O master.tar.xz
tar -xf master.tar.xz
mv kivy-kivent-* kivy-kivent
cd kivy-kivent/modules/core/
../../../env/bin/python setup.py install
cd -
rm -f master.tar.xz
rm -rf kivy-kivent


