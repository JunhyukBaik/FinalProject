#!/bin/bash

mkdir templates
mkdir upload

pip3 install Flask
pip3 install requests
pip3 install bs4
pip3 install numpy
pip install -U Werkzeug

if [ -f "URLresult.html" ]; then
	mv URLresult.html templates
fi


if [ -f "OSP_finhome.html" ]; then
	mv OSP_finhome.html templates
fi


echo Starting...
flask run

