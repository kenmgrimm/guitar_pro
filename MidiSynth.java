import java.io.*;

import javax.sound.midi.*;

class MidiSynth {

  public static void main(String[] args) {
    InputStreamReader isReader = new InputStreamReader(System.in);
    BufferedReader bufReader = new BufferedReader(isReader);

    int channel = 1; // 0 is a piano, 9 is percussion, other channels are for other instruments

    int volume = 126; // between 0 et 127

    try {
      Synthesizer synth = MidiSystem.getSynthesizer();

      // Soundbank soundbank = synth.getDefaultSoundbank();
      // Instrument[] instruments = soundbank.getInstruments();

      // Instrument instrument = instruments[1];

      synth.open();

      MidiChannel[] channels = synth.getChannels();
      MidiChannel mc = channels[channel];

      // BufferedInputStream soundBankStream = new BufferedInputStream(
       // MidiSynth.class.getClassLoader().getResourceAsStream("/data/projects/guitar_pro/soundbank-deluxe.gm"));

      // synth.loadAllInstruments(MidiSystem.getSoundbank(soundBankStream));

      // soundBankStream.close()

      Soundbank soundbank = synth.getDefaultSoundbank();
      Instrument[] instruments = soundbank.getInstruments();

      Instrument instrument = instruments[17];


      synth.loadInstrument(instrument);

      mc.programChange(instrument.getPatch().getProgram());

        while (true) {
          try {
            String inputStr = null;
            if ((inputStr = bufReader.readLine()) != null) {
              String[] notes = inputStr.split(", ");
              int duration = 0;

              for(int i = 0; i < notes.length; i++) {
                String[] nd = notes[i].split(":");
                duration = Integer.parseInt(nd[1]);
                mc.noteOn(Integer.parseInt(nd[0]), volume);
              }


              Thread.sleep(duration);

              for(int i = 0; i < notes.length; i++) {
                String[] nd = notes[i].split(":");
                mc.noteOff(Integer.parseInt(nd[0]), volume);
              }
              
            } 
          } catch (Exception e) {
            System.out.println(e);
          }
        }

// movie of dream sequences one after another from a person in VR.  Cuts back to reality in very quick intervals where the person 

    } catch (Exception e) {
      e.printStackTrace();

    }


  }
}
