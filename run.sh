#!/bin/bash

echo 'Set audio with(where n is 0=auto, 1=headphones, 2=hdmi):  sudo amixer -c 0 cset numid=3 1'

# MAKE SURE TO KILL ZOMBIE JAVA
javac MidiSynth.java && python play.py 2> error.log ; reset ; killall java

