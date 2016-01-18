from os import path

import subprocess

import sys
import time
import curses
from subprocess import Popen, PIPE

import guitarpro

# import led_midi


START = 100
song_file = 'Rush - Spirit Of The Radio.gp5'
# song_file = 'the_rain_song.gp5'
# song_file =	'since_ive_been_loving_you.gp3'
# song_file = 'mediterranean_sundance.gp5'
# song_file = 'entre_dos_aguas.gp3'
# START = 170

ch = ''

# TEMPO_PERCENT = 100
TEMPO_PERCENT = 0.0004

TAB_LINE_LENGTH = 40 
TAB_HEIGHT = 50

def currentTime():
  return int(round(time.time() * TEMPO_PERCENT * 1000)) 


START_TIME = currentTime()

myscreen = curses.initscr()
myscreen.timeout(1)

midiSynth = subprocess.Popen(['java', 'MidiSynth'], stdin = subprocess.PIPE)

if curses.COLS < TAB_LINE_LENGTH or curses.LINES < TAB_HEIGHT:
  sys.stderr.write("Screen size too small: " + str(curses.COLS) + "x" + str(curses.LINES) + "\n")
  sys.stderr.write("Screen size should be at least: " + str(TAB_LINE_LENGTH) + "x" + str(TAB_HEIGHT) + "\n\n\n")
  exit()

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


class Tick:

	def __init__(self, startMs):
		self.setup(startMs, [-1, -1, -1, -1, -1, -1])	

	def setup(self, startMs, strings):
		self.startMs = startMs
		self.strings = strings
		self.realNoteValues = []
		# print "setup: " + str(self.strings)


	def update(self, string, fret, realNoteValue, duration):
		# print "update: " + str(string) + ", " + str(fret)
		# print "update: " + str(self.strings)
		self.strings[string - 1] = fret
		self.realNoteValues.append(realNoteValue)

		### NOTE:  using same duration for all notes in a chord(see where this is called)
		self.duration = duration

class Tab:

	def __init__(self):
		self.ticks = []
		self.playIndex = 0
		self.playTime = 0

	def appendTabTick(self, startMs, string, fret, realNoteValue, duration):
		if len(self.ticks) > 0:
			lastTick = self.ticks[-1]

			if startMs == lastTick.startMs:
				lastTick.update(string, fret, realNoteValue, duration)
			else:
				newTick = Tick(startMs)
				newTick.update(string, fret, realNoteValue, duration)
				self.ticks.append(newTick)
		else:
			newTick = Tick(startMs)
			newTick.update(string, fret, realNoteValue, duration)
			self.ticks.append(newTick)

	def startSegmentNumber(self):
		segmentNumber = self.playIndex / TAB_LINE_LENGTH
		return int(segmentNumber / 5) * 5


	def printLines(self, startMs, lastMs):
		currentLineNumber = 2
		segmentNumber = self.startSegmentNumber()
		endSegmentNumber = segmentNumber + 4

		# print "Lines: " + str(segmentNumber) + " - " + str(endSegmentNumber)

		while segmentNumber * TAB_LINE_LENGTH + segmentNumber < len(self.ticks):
			if segmentNumber > endSegmentNumber: 
				break

			startPos = segmentNumber * TAB_LINE_LENGTH
			endPos = startPos + TAB_LINE_LENGTH

			segment = self.ticks[startPos : endPos]

			for lineNumber in range(6):
				line = []

				for tick in segment:
					fret = self.translateFret(tick.strings[lineNumber])
					line.append(str(fret))

				myscreen.addstr(currentLineNumber, 4, '- '.join(line))
				currentLineNumber += 1

			if self.playIndex >= startPos and self.playIndex < endPos:
				frontPadLength = self.playIndex - startPos
				endPadLength = endPos - self.playIndex - 1

				myscreen.addstr(currentLineNumber, 0, ' ' * frontPadLength  * 4 + '^' + ' ' * endPadLength * 4)
				currentLineNumber += 1
			else:
				myscreen.addstr(currentLineNumber, 1, "")
				currentLineNumber += 1

			myscreen.addstr(currentLineNumber, 1, "")
			currentLineNumber += 1

			segmentNumber += 1
			# for segmentStart in xrange(0, len(line), TAB_LINE_LENGTH):
			# 	segment = yield line[segmentStart:segmentStart + TAB_LINE_LENGTH]
			# 	print ' '.join(segment)
		myscreen.addstr(currentLineNumber, 1, "  " + str(startMs * TEMPO_PERCENT - lastMs * TEMPO_PERCENT) + ", " + ch)
		currentLineNumber += 1
		
		myscreen.refresh()

	def play(self):
		self.playIndex = START

		lastMs = 0
		index = self.playIndex

		startTime = self.ticks[self.playIndex].startMs

		while index < len(self.ticks):
			sys.stderr.write("got: " + str(index) + "  ")

			tick = self.ticks[index]

			if lastMs == -1:
				lastMs = self.ticks[index - 1].startMs - startTime
				sys.stderr.write("last now: " + str(lastMs))

			self.printLines(tick.startMs, lastMs)

			notes = []
			for note in tick.realNoteValues:
				notes.append(str(note) + ":" + str(int(tick.duration * TEMPO_PERCENT * 1000)))
				print str(tick.duration * TEMPO_PERCENT)

			midiSynth.stdin.write(', '.join(map(str, notes)) + "\n")

			time.sleep((tick.startMs - startTime) * TEMPO_PERCENT - lastMs * TEMPO_PERCENT)

			ch = myscreen.getch()

			# sys.stderr.write("got: " + str(ch) + "  ")
			lastMs = tick.startMs - startTime

			self.playIndex += 1
			index += 1


			### Attempt at forward, rewind

			if ch == 27:
				# self.playIndex -= 10
				index -= 10
				lastMs = -1
				self.playIndex -= 10
			elif ch == 91:
				# self.playIndex += 10
				index -= 10
				lastMs = -1
				self.playIndex -= 10

			if index < 0: index = 0
			if self.playIndex < 0: self.playIndex = 0

			sys.stderr.write("new vals: " + str(index) + ", " + str(lastMs))

			# self.playIndex += 10



			curses.endwin()



	def chunks(self, line, segmentLength):
		for i in xrange(0, len(line), segmentLength):
			yield line[i:i + segmentLength]

	def translateFret(self, fret):
		char = str(fret) if fret != -1 else '-'
		if fret < 10: char += ' '
		return char

def main():

	# curs_set(0)

	myscreen.border(0)

	filepath = path.join(song_file)
	song = guitarpro.parse(filepath)

	tab = Tab()

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

	# tab.printLines()

	tab.play()

	midiSynth.close()


def eventStartTime(event):
	return event.realStartTime


if __name__ == '__main__':
  main()

