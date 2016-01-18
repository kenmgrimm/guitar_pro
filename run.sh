#!/bin/bash

javac MidiSynth.java && python translate_gp.py 2> test.txt ; reset ; killall java

