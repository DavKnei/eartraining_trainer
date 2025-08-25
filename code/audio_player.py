import os
import json
from pydub import AudioSegment
from pydub.playback import play

class AudioPlayer:
    """
    Handles loading audio samples and playing harmonica licks.
    """
    def __init__(self, samples_base_path="audio_samples"):
        self.samples_base_path = samples_base_path
        self.harmonica_samples = {}
        self.metadata = self._load_metadata()
        print("AudioPlayer initialized.")

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

            # --- NEW LOGIC IS HERE ---
            if tab == "rest":
                # If the tab is a rest, just add silence.
                final_sequence += AudioSegment.silent(duration=note_duration_ms)
            else:
                # Otherwise, do what we did before: find and play the sample.
                sample = self.harmonica_samples.get(tab)
                if sample is None:
                    print(f"Warning: Sample for tab '{tab}' not found. Treating as a rest.")
                    final_sequence += AudioSegment.silent(duration=note_duration_ms)
                    continue
                
                played_note = sample[:note_duration_ms]
                final_sequence += played_note
            # --- END OF NEW LOGIC ---

        print(f"Playing lick at {bpm} BPM...")
        play(final_sequence)


# --- Example of how to use this class ---
if __name__ == "__main__":
    # This is a test block to make sure our player works.
    
    # 1. Create an instance of the player
    player = AudioPlayer()

    # 2. Load the samples for the harmonica we want to use (e.g., a G harp)
    player.load_harp_samples('G')

    # 3. Define a sample lick to test with
    # This is the "Simple Blues Turnaround" from your licks file
    test_lick = [
        {"tab": "-2", "duration": 1},
        {"tab": "-3_p", "duration": 0.5},
        {"tab": "rest", "duration": 0.5},
        {"tab": "4", "duration": 0.5},
        {"tab": "-3_p", "duration": 0.5},
        {"tab": "rest", "duration": 0.5},
        {"tab": "-2", "duration": 1.5}
    ]

    # 4. Play the lick at a desired speed
    player.play_lick(test_lick, bpm=100)
    
    # 5. Play it again, faster
    player.play_lick(test_lick, bpm=160)