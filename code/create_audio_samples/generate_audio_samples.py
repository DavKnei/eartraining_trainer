import os
import math
import json
import yaml
from pydub import AudioSegment
from pydub.generators import Sine

# --- 1. GLOBAL CONFIGURATION ---

# List of harmonica keys you want to generate samples for.
KEYS_TO_GENERATE = ['G', 'A', 'C', 'D'] 
OUTPUT_FOLDER = "audio_samples"
TUNING_FILE = 'tunings.yaml'
DEFAULT_TUNING = 'richter'
SAMPLE_DURATION_MS = 2000  # 2 seconds is a good length
ATTACK_MS = 15
RELEASE_MS = 100
NUM_HARMONICS = 8

# --- 2. MUSIC THEORY ENGINE ---

# Defines the 12 notes in an octave. Used for note calculation.
SEMITONES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Base frequency for all calculations (A4 = 440 Hz)
A4_FREQ = 440.0
# The position of A in our SEMITONES list
A4_INDEX = 9
# The octave of our reference note
A4_OCTAVE = 4

# --- 3. HELPER FUNCTIONS ---

def load_tuning(file_path=TUNING_FILE, tuning_name=DEFAULT_TUNING):
    """Loads a specific tuning layout from the YAML file."""
    try:
        with open(file_path, 'r') as f:
            all_tunings = yaml.safe_load(f)
            print(f"Successfully loaded tuning '{tuning_name}' from {file_path}")
            return all_tunings['tunings'][tuning_name]
    except FileNotFoundError:
        print(f"❌ ERROR: Tuning file not found at {file_path}")
        return None
    except KeyError:
        print(f"❌ ERROR: Tuning '{tuning_name}' not found in {file_path}")
        return None

def get_note_name_and_freq(root_note_index, octave, semitone_offset):
    """Calculates a note's name, octave, and frequency based on an offset from a root note."""
    total_offset = root_note_index + semitone_offset
    note_octave = octave + (total_offset // 12)
    note_index = total_offset % 12
    note_name = f"{SEMITONES[note_index]}{note_octave}"

    # Calculate frequency relative to A4
    num_semitones_from_a4 = (note_octave - A4_OCTAVE) * 12 + note_index - A4_INDEX
    frequency = A4_FREQ * (2**(num_semitones_from_a4 / 12.0))
    
    return note_name, frequency

def get_tab_name(hole, action, bend_level=0):
    """Creates the file-safe tab name like '-2' or '-3_pp' for a double bend."""
    if action == 'blow':
        return str(hole)
    elif action == 'draw':
        if bend_level == 0:
            return f"-{hole}"
        else:
            # e.g., -2', -3'', etc. -> -2_p, -3_pp
            return f"-{hole}_{'p' * bend_level}"

# --- 4. AUDIO GENERATION ---

def generate_harmonica_tone(frequency, duration_ms):
    """Generates a complex tone with harmonics to simulate a harmonica."""
    fundamental = Sine(frequency).to_audio_segment(duration=duration_ms)
    combined_tone = fundamental
    for i in range(2, NUM_HARMONICS + 1):
        harmonic_freq = frequency * i
        # This falloff is key to the final timbre.
        gain_db = -6.0 * math.log2(i)
        harmonic = Sine(harmonic_freq).to_audio_segment(duration=duration_ms).apply_gain(gain_db)
        combined_tone = combined_tone.overlay(harmonic)
    return combined_tone

# --- 5. MAIN SCRIPT LOGIC ---

def generate_all_samples():
    """
    Main function to generate all notes for the specified harmonica keys
    and create a JSON file with all the metadata.
    """
    # Load the tuning layout from the external file
    tuning_layout = load_tuning()
    if not tuning_layout:
        print("Halting generation due to tuning load error.")
        return

    harmonica_metadata = {}
    print("\nStarting audio sample generation process...")

    for key in KEYS_TO_GENERATE:
        print(f"\n--- Processing Key: {key} Harmonica ---")
        
        key_folder_name = f"{key}_harp"
        key_output_path = os.path.join(OUTPUT_FOLDER, key_folder_name)
        if not os.path.exists(key_output_path):
            os.makedirs(key_output_path)
            
        # Get the root note index (e.g., 'G' is index 7) and starting octave
        root_note_index = SEMITONES.index(key)
        # Lower keys like G and A start in a lower octave
        start_octave = 3 if key in ['G', 'A'] else 4

        harmonica_metadata[key] = {}

        # Use .items() to iterate through holes and their actions
        for hole, actions in tuning_layout.items():
            # Process Blow Note
            note_name, freq = get_note_name_and_freq(root_note_index, start_octave, actions['blow'])
            tab = get_tab_name(hole, 'blow')
            harmonica_metadata[key][tab] = {'note': note_name, 'frequency': round(freq, 2)}
            _generate_and_save_sample(freq, key_folder_name, tab)

            # Process Draw Note
            note_name, freq = get_note_name_and_freq(root_note_index, start_octave, actions['draw'])
            tab = get_tab_name(hole, 'draw')
            harmonica_metadata[key][tab] = {'note': note_name, 'frequency': round(freq, 2)}
            _generate_and_save_sample(freq, key_folder_name, tab)

            # Process Bends if they exist for the hole
            if 'bends' in actions:
                for i, bend_offset in enumerate(actions['bends'], 1):
                    draw_note_offset = actions['draw']
                    note_name, freq = get_note_name_and_freq(root_note_index, start_octave, draw_note_offset + bend_offset)
                    tab = get_tab_name(hole, 'draw', bend_level=i)
                    harmonica_metadata[key][tab] = {'note': note_name, 'frequency': round(freq, 2)}
                    _generate_and_save_sample(freq, key_folder_name, tab)

    # Write all collected metadata to a JSON file
    json_path = os.path.join(OUTPUT_FOLDER, "harmonica_data.json")
    with open(json_path, 'w') as f:
        json.dump(harmonica_metadata, f, indent=2)
    print(f"\n✅ Success! Metadata saved to {json_path}")
    print("All samples generated.")

def _generate_and_save_sample(frequency, key_folder, tab_name):
    """Helper to generate and save a single audio file."""
    filename = f"{tab_name}.wav"
    filepath = os.path.join(OUTPUT_FOLDER, key_folder, filename)

    if os.path.exists(filepath):
        # This check prevents re-generating files, saving time.
        # To re-generate all files, delete the audio_samples folder first.
        return

    # Generate the complex tone
    harmonica_wave = generate_harmonica_tone(frequency, SAMPLE_DURATION_MS)
    
    # Apply fade in/out and normalize volume to prevent clipping
    final_wave = harmonica_wave.fade_in(ATTACK_MS).fade_out(RELEASE_MS).normalize()
    
    # Export the final audio to a .wav file
    final_wave.export(filepath, format="wav")
    print(f"  -> Created: {filepath}")


if __name__ == "__main__":
    generate_all_samples()