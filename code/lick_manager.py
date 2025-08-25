import os
import json
import random

class LickManager:
    """
    Handles loading licks from a directory of scale-based JSON files.
    The first three licks in each file are assumed to be the low, middle,
    and high register scales, respectively.
    """
    def __init__(self, licks_directory="licks"):
        self.directory = licks_directory
        self.licks = []
        self.loaded_scale = None
        self.available_scales = self._discover_scales()
        
        if self.available_scales:
            print(f"LickManager initialized. Found scales: {', '.join(self.available_scales)}")
            self.load_licks_for_scale(self.available_scales[0])
        else:
            print("Warning: No lick files found in the 'licks' directory.")

    def _discover_scales(self):
        """Scans the licks directory and finds all available scale files."""
        try:
            files = [f for f in os.listdir(self.directory) if f.endswith('.json')]
            return sorted([os.path.splitext(f)[0] for f in files])
        except FileNotFoundError:
            return []

    def load_licks_for_scale(self, scale_name):
        """Loads all licks from a specific scale's JSON file into memory."""
        filepath = os.path.join(self.directory, f"{scale_name}.json")
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.licks = data.get("licks", [])
                self.loaded_scale = scale_name
                print(f"Successfully loaded {len(self.licks)} total entries for scale: {scale_name}")
                return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"ERROR loading {filepath}: {e}")
            self.licks = []
            return False

    def get_available_scales(self):
        """Returns the list of discovered scale names."""
        return self.available_scales

    def get_scale_by_register(self, register):
        """
        Returns the specific scale part based on the selected register.
        Assumes a fixed order: low (index 0), middle (1), high (2).
        """
        register_map = {"low": 0, "middle": 1, "high": 2}
        index = register_map.get(register)
        
        if index is not None and len(self.licks) > index:
            return self.licks[index]
        return None

    def get_random_lick(self, register="all"):
        """
        Returns a random practice lick and its original index, optionally
        filtered by register.

        Returns
        -------
        tuple or None
            A tuple containing the lick object and its index, or None.
        """
        if len(self.licks) <= 3:
            return None 

        selectable_licks_with_indices = list(enumerate(self.licks))[3:]
        if not selectable_licks_with_indices:
            return None

        if register != "all":
            filtered_licks = [(i, lick) for i, lick in selectable_licks_with_indices if lick.get("register") == register]
            if not filtered_licks:
                return None 
            
            original_index, lick_obj = random.choice(filtered_licks)
            return lick_obj, original_index
        
        original_index, lick_obj = random.choice(selectable_licks_with_indices)
        return lick_obj, original_index