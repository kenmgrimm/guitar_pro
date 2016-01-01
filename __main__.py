from os import path

import guitarpro
import tests


def main():
    for test in tests.TESTS:
        filepath = path.join(tests.LOCATION, test)
        song = guitarpro.parse(filepath)

	for track in song.tracks:
		print "Name: " + track.name
		for measure in track.measures:
			for voice in measure.voices:
                		for beat in voice.beats:
					print "Beat start: " + str(beat.start) + ", duration: " + str(beat.duration.value) + ", " + str(beat.__dict__)
					if beat.effect.chord is not None:
						print "Chord: " + str(beat.effect.chord.name) + str(beat.effect.chord.strings) + str(beat.effect.chord.fingerings)
                    			for note in beat.notes:
						print str(note.type) + ", " + str(note.effect) + ", " + str(note.string) + ": " + str(note.value) + ", real: " + str(note.realValue)
						#print note.value
	

if __name__ == '__main__':
    main()
