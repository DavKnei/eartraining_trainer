import os
import json
from pydub import AudioSegment
from pydub.playback import play
import threading
import time

class AudioPlayer:
    """
    Handles loading audio samples and playing harmonica licks.
    """
    def __init__(self, samples_base_path="audio_samples"):
        self.samples_base_path = samples_base_path
        self.harmonica_samples = {}
        self.metadata = self._load_metadata()
        self.metronome_click_1 = None
        self.metronome_click_2 = None
        self._load_metronome_sounds()
        self.stop_call_and_response = False
        print("AudioPlayer initialized.")

    def _load_metronome_sounds(self):
        """Loads both metronome click sounds."""
        metronome_path_1 = os.path.join(self.samples_base_path, "metronome_click1.wav")
        metronome_path_2 = os.path.join(self.samples_base_path, "metronome_click.wav")

        if os.path.exists(metronome_path_1):
            self.metronome_click_1 = AudioSegment.from_wav(metronome_path_1)
        else:
            print(f"Warning: Metronome click 1 sound not found at {metronome_path_1}")

        if os.path.exists(metronome_path_2):
            self.metronome_click_2 = AudioSegment.from_wav(metronome_path_2)
        else:
            print(f"Warning: Metronome click 2 sound not found at {metronome_path_2}")

    def _load_metadata(self):
        """Loads the harmonica metadata from the JSON file."""
        metadata_path = os.path.join(self.samples_base_path, "harmonica_data.json")
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Metadata file not found at {metadata_path}")
            return None

    def load_harp_samples(self, key='G'):
        """
        Loads all .wav samples for a specific harmonica key into memory.
        """
        self.harmonica_samples.clear() # Clear any previously loaded harp
        harp_folder = f"{key.upper()}_harp"
        key_path = os.path.join(self.samples_base_path, harp_folder)

        if not os.path.exists(key_path):
            print(f"Error: Sample directory not found for key {key} at {key_path}")
            return False

        print(f"Loading samples for {key} harmonica...")
        for filename in os.listdir(key_path):
            if filename.endswith(".wav"):
                tab_name = filename.replace('.wav', '')
                sample_path = os.path.join(key_path, filename)
                self.harmonica_samples[tab_name] = AudioSegment.from_wav(sample_path)
        
        print(f"Loaded {len(self.harmonica_samples)} samples.")
        return True

    def play_lick(self, lick_data, bpm=120):
        """
        Plays a lick by sequencing the loaded audio samples.
        Now handles rests.

        :param lick_data: A list of note dictionaries, e.g., [{"tab": "-2", "duration": 1}, ...]
        :param bpm: The speed of the lick in beats per minute.
        """
        if not self.harmonica_samples:
            print("Error: No harmonica samples loaded. Call load_harp_samples() first.")
            return

        quarter_note_duration_ms = 60000 / bpm
        final_sequence = AudioSegment.silent(duration=0)

        for note in lick_data:
            tab = note['tab']
            duration_in_beats = note['duration']
            note_duration_ms = int(quarter_note_duration_ms * duration_in_beats)

            if tab == "rest":
                final_sequence += AudioSegment.silent(duration=note_duration_ms)
            else:
                sample = self.harmonica_samples.get(tab)
                if sample is None:
                    print(f"Warning: Sample for tab '{tab}' not found. Treating as a rest.")
                    final_sequence += AudioSegment.silent(duration=note_duration_ms)
                    continue
                
                played_note = sample[:note_duration_ms]
                final_sequence += played_note

        print(f"Playing lick at {bpm} BPM...")
        play(final_sequence)

    def play_call_and_response(self, lick_data, bpm=120, time_signature_str="4/4"):
        """
        Plays a lick in a call-and-response loop with an accented metronome,
        using the time signature from the lick data.
        """
        if not self.harmonica_samples:
            print("Error: No harmonica samples loaded.")
            return

        if not self.metronome_click_1 or not self.metronome_click_2:
            print("Error: Metronome sounds not loaded.")
            return
        
        try:
            beats_per_measure, _ = map(int, time_signature_str.split('/'))
        except (ValueError, IndexError):
            print(f"Warning: Invalid time signature '{time_signature_str}'. Defaulting to 4/4.")
            beats_per_measure = 4

        quarter_note_duration_ms = 60000 / bpm
        total_duration_beats = sum(note['duration'] for note in lick_data)

        # Create the "call" part (the lick)
        call_part = AudioSegment.silent(duration=0)
        for note in lick_data:
            tab = note['tab']
            duration_in_beats = note['duration']
            note_duration_ms = int(quarter_note_duration_ms * duration_in_beats)

            if tab == "rest":
                call_part += AudioSegment.silent(duration=note_duration_ms)
            else:
                sample = self.harmonica_samples.get(tab)
                if sample:
                    call_part += sample[:note_duration_ms]
                else:
                    call_part += AudioSegment.silent(duration=note_duration_ms)
        
        # Create the "response" part (metronome clicks)
        response_part = AudioSegment.silent(duration=0)
        num_beats_total = int(total_duration_beats)
        
        for i in range(num_beats_total):
            beat_in_measure = i % beats_per_measure
            
            if beat_in_measure == 0:
                click = self.metronome_click_1 # First beat
            else:
                click = self.metronome_click_2 # Other beats
            
            response_part += click[:int(quarter_note_duration_ms)]

        # The loop
        self.stop_call_and_response = False
        while not self.stop_call_and_response:
            play(call_part)
            if self.stop_call_and_response:
                break
            play(response_part)