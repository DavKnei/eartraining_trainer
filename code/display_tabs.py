import os
import json
from music21 import stream, note, meter, environment

# Base path for the score image. The final path will be returned by music21.
SCORE_IMAGE_BASENAME = "temp_score"

def format_single_tab(tab_string):
    """
    Converts a single file-safe tab name to a display-friendly name.
    
    Parameters
    ----------
    tab_string : str
        The file-safe tab name (e.g., '-3_p', '-2_pp').

    Returns
    -------
    str
        The display-friendly tab name (e.g., "-3'", "-2''").
    """
    if '_pp' in tab_string:
        return tab_string.replace('_pp', "''")
    if '_p' in tab_string:
        return tab_string.replace('_p', "'")
    return tab_string

class NotationGenerator:
    """
    Handles the conversion of lick data into a musical score image with embedded tabs.
    """
    def __init__(self, metadata_path="audio_samples/harmonica_data.json"):
        self.harmonica_data = self._load_metadata(metadata_path)
        self.env = environment.UserSettings()

    def _load_metadata(self, path):
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
                    # NEW: Format the single tab and add it as a lyric to the note
                    display_tab = format_single_tab(tab)
                    n.addLyric(f" {display_tab}")
                else:
                    print(f"Warning: Note for tab '{tab}' in key '{harp_key}' not found.")
                    n = note.Rest(quarterLength=duration)
            
            part.append(n)

        score.append(part)
        
        try:
            # MODIFIED: Let music21 return the actual path it wrote to.
            # This handles cases where it adds "_1", etc.
            image_path = score.write('musicxml.png', fp=SCORE_IMAGE_BASENAME)
            return image_path
        except Exception as e:
            print(f"Error generating score image. Is MuseScore installed and configured? Error: {e}")
            return None
