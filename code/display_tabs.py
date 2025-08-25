import os
import json
import uuid  # NEW: Import the module for generating unique IDs
from music21 import stream, note, meter, environment

class NotationGenerator:
    """
    Handles the conversion of lick data into a musical score image with embedded tabs.
    """
    def __init__(self, metadata_path="audio_samples/harmonica_data.json"):
        self.harmonica_data = self._load_metadata(metadata_path)
        self.env = environment.UserSettings()

    def _load_metadata(self, path):
        """Loads the harmonica metadata from the JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Harmonica metadata not found at {path}")
            return {}

    def generate_score_image(self, lick_data, time_signature_str, harp_key):
        """
        Creates a PNG image of a musical score from lick data with tabs as lyrics.
        
        Returns
        -------
        str or None
            The path to the generated image, or None if generation failed.
        """
        if not self.harmonica_data:
            return None

        score = stream.Score()
        part = stream.Part()
        part.append(meter.TimeSignature(time_signature_str))

        for note_info in lick_data:
            duration = note_info['duration']
            tab = note_info['tab']
            
            if tab == 'rest':
                n = note.Rest(quarterLength=duration)
            else:
                note_name = self.harmonica_data.get(harp_key, {}).get(tab, {}).get('note')
                if note_name:
                    n = note.Note(note_name, quarterLength=duration)
                    display_tab = self._format_single_tab(tab)
                    # Add a space before the tab to prevent hyphenation issues in older music21 versions
                    n.addLyric(f" {display_tab}")
                else:
                    print(f"Warning: Note for tab '{tab}' in key '{harp_key}' not found.")
                    n = note.Rest(quarterLength=duration)
            
            part.append(n)

        score.append(part)
        
        try:
            # MODIFIED: Generate a unique basename for the temporary file
            temp_basename = f"temp_score_{uuid.uuid4()}"
            image_path = score.write('musicxml.png', fp=temp_basename)
            return image_path
        except Exception as e:
            print(f"Error generating score image. Is MuseScore installed and configured? Error: {e}")
            return None

    def _format_single_tab(self, tab_string):
        """
        Converts a single file-safe tab name to a display-friendly name.
        (Internal helper method)
        """
        if '_pp' in tab_string:
            return tab_string.replace('_pp', "''")
        if '_p' in tab_string:
            return tab_string.replace('_p', "'")
        return tab_string