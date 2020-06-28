#!/bin/bash

mkdir templates
mkdir uploads

pip3 install Flask
pip3 install requests
pip3 install bs4
pip3 install numpy

echo Starting...
flask run

