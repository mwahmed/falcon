#!/bin/bash

echo "Installing Requests; should be run as su"

curl -OL https://github.com/kennethreitz/requests/tarball/master
tar -zxf master
cd kennethreitz-requests-99ebac7
python setup.py install
cd ..
rm master
rm -rf kennethreitz-requests-99ebac7
