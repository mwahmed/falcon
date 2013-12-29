#!/bin/bash

echo "Installing audiolabs"
apt-get install python-dev python-numpy python-setuptools libsndfile-dev

sudo aptitude install flac vorbis-tools
#wget -O audiolab.tar.gz https://pypi.python.org/packages/source/s/scikits.audiolab/scikits.audiolab-0.11.0.tar.gz
#tar -zxf audiolab.tar.gz
cd scikits.audiolab-0.11.0
python setup.py build
python setup.py install
