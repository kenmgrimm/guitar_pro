#!/bin/bash

echo 'Set audio with(where n is 0=auto, 1=headphones, 2=hdmi):  sudo amixer -c 0 cset numid=3 1'

javac MidiSynth.java && python translate_gp.py 2> translate_gp.err ; reset ; killall java

