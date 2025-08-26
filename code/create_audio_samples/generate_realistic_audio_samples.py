import os
import math
import json
import yaml
from pydub import AudioSegment
from pydub.silence import split_on_silence

# --- 1. GLOBAL CONFIGURATION ---

KEYS_TO_GENERATE = ['G', 'A', 'C', 'D']
OUTPUT_FOLDER = "../audio_samples"
MASTER_SAMPLES_FOLDER = "master_samples"
TUNING_FILE = 'tunings.yaml'
DEFAULT_TUNING = 'richter'
SAMPLE_DURATION_MS = 2000
ATTACK_MS = 10
RELEASE_MS = 200

# --- 2. MUSIC THEORY ENGINE ---

SEMITONES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
A4_FREQ = 443.0
A4_INDEX = 9
A4_OCTAVE = 4

# --- 3. HELPER FUNCTIONS ---

def load_tuning(file_path=TUNING_FILE, tuning_name=DEFAULT_TUNING):
    """Loads a specific tuning layout from the YAML file."""
    try:
        with open(file_path, 'r') as f:
            all_tunings = yaml.safe_load(f)
            print(f"Successfully loaded tuning '{tuning_name}' from {file_path}")
            return all_tunings['tunings'][tuning_name]
    except (FileNotFoundError, KeyError) as e:
        print(f"❌ ERROR loading tuning: {e}")
        return None

def get_note_name_and_freq(root_note_index, octave, semitone_offset):
    """Calculates a note's name, octave, and frequency."""
    total_offset = root_note_index + semitone_offset
    note_octave = octave + (total_offset // 12)
    note_index = total_offset % 12
    note_name = f"{SEMITONES[note_index]}{note_octave}"
    num_semitones_from_a4 = (note_octave - A4_OCTAVE) * 12 + note_index - A4_INDEX
    frequency = A4_FREQ * (2**(num_semitones_from_a4 / 12.0))
    return note_name, frequency

def get_tab_name(hole, action, bend_level=0):
    """Creates the file-safe tab name."""
    if action == 'blow':
        return str(hole)
    elif action == 'draw':
        bend_suffix = f"_{'p' * bend_level}" if bend_level > 0 else ""
        return f"-{hole}{bend_suffix}"

# --- 4. SAMPLE-BASED AUDIO GENERATION ---

def trim_and_normalize(audio_segment):
    """Trims silence from start/end and normalizes the audio."""
    # Find non-silent chunks
    chunks = split_on_silence(audio_segment, min_silence_len=100, silence_thresh=-50)
    if not chunks:
        return AudioSegment.silent(duration=0) # Return silent if no sound
    
    # Concatenate non-silent chunks and normalize
    processed_audio = sum(chunks, AudioSegment.silent(duration=0))
    return processed_audio.normalize()

def pitch_shift(sound, target_freq, source_freq):
    """Pitch-shifts an AudioSegment."""
    if source_freq == 0: return sound # Avoid division by zero
    
    octaves = math.log2(target_freq / source_freq)
    
    # In pydub, you can change the framerate to shift pitch
    new_frame_rate = int(sound.frame_rate * (2.0 ** octaves))
    return sound._spawn(sound.raw_data, overrides={'frame_rate': new_frame_rate})


def load_master_samples(master_sample_path, metadata):
    """Loads, cleans, and stores the master samples."""
    print(f"\n--- Loading and Processing Master Samples from {master_sample_path} ---")
    master_samples = {}
    
    # We only need the G harp metadata for the original frequencies
    g_harp_data = metadata.get('G', {})
    if not g_harp_data:
        print("❌ ERROR: Could not find 'G' harp data in metadata to get master sample frequencies.")
        return None

    for filename in os.listdir(master_sample_path):
        if filename.endswith(".wav"):
            tab_name = filename.replace('.wav', '')
            filepath = os.path.join(master_sample_path, filename)
            
            try:
                original_sound = AudioSegment.from_wav(filepath)
                # Clean up the sample
                clean_sound = trim_and_normalize(original_sound)
                
                # Get the original frequency from our metadata
                source_freq = g_harp_data.get(tab_name, {}).get('frequency')

                if source_freq:
                    master_samples[tab_name] = {
                        'audio': clean_sound,
                        'freq': source_freq
                    }
                    print(f"  -> Loaded and processed master sample: {filename} (Freq: {source_freq} Hz)")
                else:
                    print(f"  ⚠️ WARNING: No frequency data found for master sample {tab_name}. Skipping.")

            except Exception as e:
                print(f"  ❌ ERROR processing {filename}: {e}")
                
    return master_samples

# --- 5. MAIN SCRIPT LOGIC ---

def find_closest_sample(target_freq, master_samples):
    """Finds the master sample with the closest frequency to the target."""
    closest_sample = None
    min_diff = float('inf')
    
    for tab, data in master_samples.items():
        diff = abs(data['freq'] - target_freq)
        if diff < min_diff:
            min_diff = diff
            closest_sample = data
            
    return closest_sample

def generate_all_samples():
    """
    Main function using multi-sampling to generate all harmonica notes.
    """
    tuning_layout = load_tuning()
    if not tuning_layout: return

    # First, we need the frequency data for our master 'G' samples
    # So we run the metadata calculation for all keys first
    full_metadata = {}
    for key in ['G', 'A', 'C', 'D']:
        root_note_index = SEMITONES.index(key)
        start_octave = 3 if key in ['G', 'A'] else 4
        key_metadata = {}
        for hole, actions in tuning_layout.items():
            for action_type in ['blow', 'draw']:
                if action_type in actions:
                    note_name, freq = get_note_name_and_freq(root_note_index, start_octave, actions[action_type])
                    tab = get_tab_name(hole, action_type)
                    key_metadata[tab] = {'note': note_name, 'frequency': round(freq, 2)}
            if 'bends' in actions:
                for i, bend_offset in enumerate(actions['bends'], 1):
                    draw_offset = actions['draw']
                    note_name, freq = get_note_name_and_freq(root_note_index, start_octave, draw_offset + bend_offset)
                    tab = get_tab_name(hole, 'draw', bend_level=i)
                    key_metadata[tab] = {'note': note_name, 'frequency': round(freq, 2)}
        full_metadata[key] = key_metadata

    # Now load the master samples using this metadata
    master_sample_path = os.path.join(OUTPUT_FOLDER, MASTER_SAMPLES_FOLDER, 'G')
    master_samples = load_master_samples(master_sample_path, full_metadata)
    if not master_samples:
        print("Halting generation: No master samples could be loaded.")
        return

    print("\n--- Generating All Note Samples ---")
    for key, key_data in full_metadata.items():
        print(f"\n--- Processing Key: {key} Harmonica ---")
        key_folder_name = f"{key}_harp"
        key_output_path = os.path.join(OUTPUT_FOLDER, key_folder_name)
        os.makedirs(key_output_path, exist_ok=True)
        
        for tab, note_data in key_data.items():
            target_freq = note_data['frequency']
            
            # Find the best master sample to start from
            closest_sample_data = find_closest_sample(target_freq, master_samples)
            
            # Pitch shift the sample
            source_audio = closest_sample_data['audio']
            source_freq = closest_sample_data['freq']
            
            final_audio = pitch_shift(source_audio, target_freq, source_freq)
            
            # Apply envelope and ensure correct length
            final_audio = final_audio[:SAMPLE_DURATION_MS].fade_in(ATTACK_MS).fade_out(RELEASE_MS)
            
            # Save the file
            filepath = os.path.join(key_output_path, f"{tab}.wav")
            final_audio.export(filepath, format="wav")
            print(f"  -> Created: {filepath} (from {source_freq}Hz to {target_freq}Hz)")


    # Write all collected metadata to a JSON file
    json_path = os.path.join(OUTPUT_FOLDER, "harmonica_data.json")
    with open(json_path, 'w') as f:
        json.dump(full_metadata, f, indent=2)
    print(f"\n✅ Success! Metadata saved to {json_path}")
    print("All samples generated.")


if __name__ == "__main__":
    generate_all_samples()