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

NO_NOTES = [-1, -1, -1, -1, -1, -1]


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
  tablature = Tablature()

  for track in song.tracks:
    print "\n\nTrack: " + track.name

    cnt = 0
    for measure in track.measures:
      for voice in measure.voices:
        events = []

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

        lastEventTime = 0
        for event in sorted(events, key = eventStartTime) :
          # while(not(event.timeToPlay())):
          #   time.sleep(0.001)
          if event.realStartTime != lastEventTime :
            tablature.appendStringState(events)
            events = []

            lastEventTime = event.realStartTime

          events.append(event)

          print event.name + " (" + str(event.realStartTime) + ") : " + str(event.note.string) + ", " + str(event.note.value) + "  (" + str(event.note.realValue) + ")"


    cnt += 1

    if cnt > 10 : break

  tablature.draw()


class Tablature:
  def __init__(self):
    self.stringStates = []

  def draw(self):
    for index in xrange(int(len(self.stringStates) / 50)) :
      rowStartPos = index * 50

      for string in [0, 1, 2, 3, 4, 5] :
        line = []
        # print "adding string " + str(string) + " rowStartPos " + str(rowStartPos)
        for stringState in self.stringStates[rowStartPos:rowStartPos + 50] :
          symbol = ' -' if stringState[string] == -1 else str(stringState[string]).rjust(2)

          line.append(symbol)

        print ''.join(line)

      print "\n\n"


  def appendStringState(self, events):
    stringState = NO_NOTES

    if len(self.stringStates) > 0 :
      stringState = list(self.stringStates[-1])

    for event in events :
      if event.__class__ is NoteOnEvent :
        # print stringState
        # print " STRING: " + str(event.note.string - 1) + " NOTE: " + str(event.note.value)
        stringState[event.note.string - 1] = event.note.value
      else :
        stringState[event.note.string - 1] = -1
        # print stringState
        # print " STRING2: " + str(event.note.string - 1) + " NOTE: " + str(event.note.value)

    self.stringStates.append(stringState)



def eventStartTime(event):
  return event.realStartTime



if __name__ == '__main__':
  main()

