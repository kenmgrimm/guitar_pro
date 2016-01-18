#!/usr/bin/env python


from os import path
import time

import guitarpro

import settings
settings.init()

import led_driver
from tablature_display import *
from midi_synthesizer import *



song_file = 'gp_files/Rush - Spirit Of The Radio.gp5'
# song_file = 'gp_files/the_rain_song.gp5'
# song_file =	'gp_files/since_ive_been_loving_you.gp3'
# song_file = 'gp_files/mediterranean_sundance.gp5'
# song_file = 'gp_files/entre_dos_aguas.gp3'


def currentTime():
  return int(round(time.time() * settings.TEMPO_PERCENT * 1000))


START_TIME = currentTime()

midiSynth = MidiSynthesizer()



class NoteOnEvent:
	def __init__(self, track, note, beat):
		self.name = 'NoteOnEvent'
		self.track = track
		self.note = note
		self.beat = beat
		self.realStartTime = beat.start + START_TIME
		# print self.name + ": " + str(beat.start) + ": " + str(START_TIME) + ": " + str(self.realStartTime)

	def timeToPlay(self):
		return currentTime() > self.realStartTime


class NoteOffEvent:
	def __init__(self, track, note, beat):
		self.name = 'NoteOffEvent'
		self.track = track
		self.note = note
		self.beat = beat
		self.realStartTime = beat.start + beat.duration.time + START_TIME

		# print self.name + ": " + str(beat.start) + ": " + str(beat.duration.time) + ": " + str(START_TIME) + ": " + str(self.realStartTime)

	def timeToPlay(self):
		return currentTime() > self.realStartTime



def main():

	# curs_set(0)

	filepath = path.join(song_file)
	song = guitarpro.parse(filepath)

	tab = Tab(midiSynth)

	for track in song.tracks:
		events = []

		for measure in track.measures:
			for voice in measure.voices:
				for beat in voice.beats:

					# print "Beat start: " + str(beat.start) + ", duration: " + str(beat.duration.time)

					if beat.effect.chord is not None:
						print "Chord: " + str(beat.effect.chord.name) + str(beat.effect.chord.strings) + str(beat.effect.chord.fingerings)

					for note in beat.notes:
						# printTabNotes()
						# print str(note.type) + ", " + str(note.effect) + ", " + str(note.string) + ": " + str(note.value) + ", real: " + str(note.realValue)

						event = NoteOnEvent(track, note, beat)
						events.append(event)

						tab.appendTabTick(beat.start, note.string, note.value, note.realValue, beat.duration.time)

						event = NoteOffEvent(track, note, beat)
						events.append(event)


			# for event in sorted(events, key = eventStartTime) :
				# while(not(event.timeToPlay())):
				# 	time.sleep(0.001)

				# print event.name + " (" + str(event.realStartTime) + ") : " + str(event.note.string) + ", " + str(event.note.value) + "  (" + str(event.note.realValue) + ")"


	tab.play()

	midiSynth.close()


def eventStartTime(event):
	return event.realStartTime


if __name__ == '__main__':
  main()

