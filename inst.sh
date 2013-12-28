#!/bin/bash


echo "Opening port 3000"
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT

echo "Opening port 8080"
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

echo "Installing audiolabs"
sudo apt-get install python-dev python-numpy python-setuptools libsndfile-dev

#wget -O audiolab.tar.gz https://pypi.python.org/packages/source/s/scikits.audiolab/scikits.audiolab-0.11.0.tar.gz
#tar -zxf audiolab.tar.gz
#cd scikits.audiolab-0.11.0
#python setup.py build
#python setup.py install
##Maybe	
##sudo aptitude install flac vorbis-tools
