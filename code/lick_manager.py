import os
import json
import random


class LickManager:
    """
    Manages loading, filtering, and providing harmonica licks from JSON files.
    """

    def __init__(self, licks_directory="licks"):
        self.licks_directory = licks_directory
        self.available_scales = self._get_available_scales()
        self.licks = []

    def _get_available_scales(self):
        """Scans the licks directory for available scale files."""
        scales = [
            f.replace(".json", "")
            for f in os.listdir(self.licks_directory)
            if f.endswith(".json")
        ]
        return sorted(scales)

    def get_available_scales(self):
        """Returns the list of available scale names."""
        return self.available_scales

    def load_licks_for_scale(self, scale_name):
        """Loads the lick data from a specified JSON file."""
        file_path = os.path.join(self.licks_directory, f"{scale_name}.json")
        try:
            with open(file_path, "r") as f:
                self.licks = json.load(f).get("licks", [])
            print(f"Loaded {len(self.licks)} licks from {scale_name}.json")
        except FileNotFoundError:
            print(f"Error: Lick file not found at {file_path}")
            self.licks = []

    def get_random_lick(self, register="all"):
        """
        Gets a random practice lick, filtering by register.
        It now returns the full lick object.
        """
        # Exclude scale definitions from the random pool
        practice_licks = [
            lick for lick in self.licks if lick.get("name", "").startswith("lick_")
        ]

        if register != "all":
            filtered_licks = [
                lick for lick in practice_licks if lick.get("register") == register
            ]
        else:
            filtered_licks = practice_licks

        if not filtered_licks:
            return None

        return random.choice(filtered_licks)

    def get_lick_by_name(self, name):
        """Finds and returns a lick object by its 'name'."""
        for lick in self.licks:
            if lick.get("name") == name:
                return lick
        return None
