
import sys
import time

import settings
import curses


myscreen = curses.initscr()
myscreen.timeout(1)

myscreen.border(0)


if curses.COLS < settings.TAB_LINE_LENGTH or curses.LINES < settings.TAB_HEIGHT:
  sys.stderr.write("Screen size too small: " + str(curses.COLS) + "x" + str(curses.LINES) + "\n")
  sys.stderr.write("Screen size should be at least: " + str(settings.TAB_LINE_LENGTH) + "x" + str(settings.TAB_HEIGHT) + "\n\n\n")
  exit()

inputKey = ''


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
  def __init__(self, midiSynth):
    self.midiSynth = midiSynth

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
    segmentNumber = self.playIndex / settings.TAB_LINE_LENGTH
    return int(segmentNumber / 5) * 5


  def play(self):
    self.playIndex = settings.START

    lastMs = 0
    index = self.playIndex

    startTime = self.ticks[self.playIndex].startMs

    while index < len(self.ticks):
      sys.stderr.write("got: " + str(index) + "  ")

      tick = self.ticks[index]

      if lastMs == -1:
        lastMs = self.ticks[index - 1].startMs - startTime
        sys.stderr.write("last now: " + str(lastMs))

      self.refreshCursesDisplay(tick.startMs, lastMs)

      notes = []
      for note in tick.realNoteValues:
        notes.append(str(note) + ":" + str(int(tick.duration * settings.TEMPO_PERCENT * 1000)))
        print str(tick.duration * settings.TEMPO_PERCENT)

      self.midiSynth.play(notes)

      time.sleep((tick.startMs - startTime) * settings.TEMPO_PERCENT - lastMs * settings.TEMPO_PERCENT)

      inputKey = myscreen.getch()

      # sys.stderr.write("got: " + str(inputKey) + "  ")
      lastMs = tick.startMs - startTime

      self.playIndex += 1
      index += 1


      ### Attempt at forward, rewind

      if inputKey == 27:
        # self.playIndex -= 10
        index -= 10
        lastMs = -1
        self.playIndex -= 10
      elif inputKey == 91:
        # self.playIndex += 10
        index -= 10
        lastMs = -1
        self.playIndex -= 10

      if index < 0: index = 0
      if self.playIndex < 0: self.playIndex = 0

      sys.stderr.write("new vals: " + str(index) + ", " + str(lastMs))

      # self.playIndex += 10



      curses.endwin()


  def refreshCursesDisplay(self, startMs, lastMs):
    currentLineNumber = 2
    segmentNumber = self.startSegmentNumber()
    endSegmentNumber = segmentNumber + 4

    # print "Lines: " + str(segmentNumber) + " - " + str(endSegmentNumber)

    while segmentNumber * settings.TAB_LINE_LENGTH + segmentNumber < len(self.ticks):
      if segmentNumber > endSegmentNumber:
        break

      startPos = segmentNumber * settings.TAB_LINE_LENGTH
      endPos = startPos + settings.TAB_LINE_LENGTH

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
      # for segmentStart in xrange(0, len(line), settings.TAB_LINE_LENGTH):
      #   segment = yield line[segmentStart:segmentStart + settings.TAB_LINE_LENGTH]
      #   print ' '.join(segment)
    myscreen.addstr(currentLineNumber, 1, "  " + str(startMs * settings.TEMPO_PERCENT - lastMs * settings.TEMPO_PERCENT) + ", " + inputKey)
    currentLineNumber += 1

    myscreen.refresh()

  def chunks(self, line, segmentLength):
    for i in xrange(0, len(line), segmentLength):
      yield line[i:i + segmentLength]

  def translateFret(self, fret):
    char = str(fret) if fret != -1 else '-'
    if fret < 10: char += ' '
    return char
