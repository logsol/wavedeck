#!/bin/bash

#python3 already installed on raspberry pi
#sudo apt-get install software-properties-common 

# tools
sudo apt-get install screen
sudo apt-get install vim

# audio dependencies
sudo apt-get install portaudio19-dev python-pyaudio python3-pyaudio
sudo apt-get install libasound2 alsa-utils alsa-oss

# pip3
sudo apt install python3-pip

# recorder dependencies
pip3 install mido
pip3 install python-rtmidi
pip3 install sounddevice
pip3 install pyaudio

# server dependencies
python3 -m pip install web.py==0.62
pip3 install zipstream
pip3 install bitmath