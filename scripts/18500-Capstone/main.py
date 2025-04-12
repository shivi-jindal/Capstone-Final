from Denoising.noise_reduction import Denoising
from Segmentation.seg import Segmentation
from Rhythm.rhythm_detection import Rhythm
from Pitch.pitch import Pitch

import pretty_midi

#new - deeya
import os 
import sys
import time
import logging
#logging.basicConfig(
#    level=logging.DEBUG,
#    format='%(asctime)s - %(levelname)s - %(message)s',
#    handlers=[
#        logging.StreamHandler(sys.stdout),  # Log to console
#        logging.FileHandler('midi_generator.log')  # Log to file
#    ]
#)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def generate_midi(audio_file_path, bpm=120, user_id=None, output_dir=None):
    BPM = int(float(bpm)) 
    #logging.debug(f"Generating MIDI with BPM: {BPM}, (type: {type(BPM)}")
    SECONDS_PER_BEAT = 60 / BPM  

    #initialize all required classes
    denoising = Denoising()
    segmentation = Segmentation()
    rhythm = Rhythm()
    pitch = Pitch()
    midi = pretty_midi.PrettyMIDI(initial_tempo=BPM)

    #pass the signal through a bandpass filter
    y_filtered, sr = denoising.noise_suppression_pipeline(audio_file_path)

    #do the note segmentation
    rms_vals, sr, og_signal, segs = segmentation.segment_notes(y_filtered, sr)

    #get the note types
    note_types = rhythm.detect_notes_lengths(rms_vals, sr, segs, BPM)

    #do pitch detection
    detected_frequencies = pitch.detect_notes(og_signal, sr, segs)
    detected_notes = [pitch.freq_to_note(f) for f in detected_frequencies] #list of note_nums

    # mapping from note type to duration
    note_durations = {"Whole Note": 4 * SECONDS_PER_BEAT, "Half Note": 2 * SECONDS_PER_BEAT, "Quarter Note": 1 * SECONDS_PER_BEAT, "Eighth Note": 0.5 * SECONDS_PER_BEAT,
                    "Sixteenth": 0.25 * SECONDS_PER_BEAT, "Whole Rest": 4 * SECONDS_PER_BEAT, "Half Rest": 2 * SECONDS_PER_BEAT, 
                    "Quarter Rest": 1 * SECONDS_PER_BEAT, "Eighth Rest": 0.5 * SECONDS_PER_BEAT, "Sixteenth Rest": 0.25 * SECONDS_PER_BEAT }

    instrument = pretty_midi.Instrument(program=73) 

    start_time = 0
    for i in range(len(detected_notes)):
        note_num = detected_notes[i]
        note_type = note_types[i]
        duration = note_durations.get(note_type, SECONDS_PER_BEAT)
        if "rest" not in note_type:
            note = pretty_midi.Note(velocity=100, pitch=note_num, start=start_time, end=start_time + duration)
            instrument.notes.append(note)
        start_time += duration  

    midi.instruments.append(instrument)

    midi_filename = f"melody_{user_id or 'anonymous'}_{int(time.time())}.mid"
    if output_dir:
        midi_path = os.path.join(output_dir, midi_filename)
    else:
        # Default to current directory if no output_dir provided
        midi_path = os.path.join(os.getcwd(), 'midi_files', midi_filename)
        os.makedirs(os.path.dirname(midi_path), exist_ok=True)
    
    midi.write(midi_path)
    result = midi_path
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        audio_file_path = sys.argv[1]
        bpm = sys.argv[2] if len(sys.argv) > 2 else 120  # Default to 120 if not provided
        user = sys.argv[3] if len(sys.argv) > 3 else "anonymous"
        result = generate_midi(audio_file_path, bpm, user)
        print(result)
    else:
        print("Error: No audio file path provided", file=sys.stderr)
        sys.exit(1)
