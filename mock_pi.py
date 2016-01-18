import os
import sys

class MockPi:

  @staticmethod
  def checkPiAndMock():
    if os.uname()[4][:3] == 'arm':
      sys.stderr.write("Running Raspberry Pi\n  os: " + ' '.join(os.uname()) + "\n\n")

      from neopixel import *
    else:
      sys.stderr.write("Not on Raspberry Pi\n  os: " + ' '.join(os.uname()) + "\n\n")

      class Strip:
        def show():
          print "showing"

        def setPixelColor(i, color):
          print "setPixelColor"

      class Color:
        def __init__(self, r, g, b):
          print "__init__"
