
import subprocess

import settings

class MidiSynthesizer:
  def __init__(self):
    self.midiSynth = subprocess.Popen(['java', 'MidiSynth'], stdin = subprocess.PIPE)

  def play(self, notes):
    self.midiSynth.stdin.write(', '.join(map(str, notes)) + "\n")

  def close(self):
    self.midiSynth.close()
