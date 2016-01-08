from os import path

import time

import guitarpro


# input guitar_pro file
#   create simple midi on / off w/ ticks
#   create simple string / fret placement w/ ticks
#   draw out tab in curses using string / frets
#   play midi along with movement of cursor in curses tab
#   add keys tempo up / down, forward / back



# TEMPO_PERCENT = 100
TEMPO_PERCENT = 0.5

def currentTime():
  return int(round(time.time() * TEMPO_PERCENT * 1000))


START_TIME = currentTime()

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


def printTabNotes():
  print "-\n-\n-\n-\n-\n-\n"

def main():
  filepath = path.join('Rush - Spirit Of The Radio.gp5')
  song = guitarpro.parse(filepath)

  for track in song.tracks:
    print "\n\nTrack: " + track.name
    events = []

    for measure in track.measures:
      for voice in measure.voices:
        for beat in voice.beats:

          print "Beat start: " + str(beat.start) + ", duration: " + str(beat.duration.time)

          if beat.effect.chord is not None:
            print "Chord: " + str(beat.effect.chord.name) + str(beat.effect.chord.strings) + str(beat.effect.chord.fingerings)

          for note in beat.notes:
            # printTabNotes()
            # print str(note.type) + ", " + str(note.effect) + ", " + str(note.string) + ": " + str(note.value) + ", real: " + str(note.realValue)

            event = NoteOnEvent(track, note, beat)
            events.append(event)

            event = NoteOffEvent(track, note, beat)
            events.append(event)


      for event in sorted(events, key = eventStartTime) :
        while(not(event.timeToPlay())):
          time.sleep(0.001)

        print event.name + " (" + str(event.realStartTime) + ") : " + str(event.note.string) + ", " + str(event.note.value) + "  (" + str(event.note.realValue) + ")"


def eventStartTime(event):
  return event.realStartTime


if __name__ == '__main__':
  main()

