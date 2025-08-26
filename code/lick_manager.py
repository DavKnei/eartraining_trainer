import os
import json
import random

class LickManager:
    """
    Handles loading licks from a directory of scale-based JSON files.
    Assumes a specific structure: all_scale, low, middle, high, mixed_combos, then practice licks.
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
            files = [f for f in os.listdir(self.directory) if f.endswith('.json') and os.path.isfile(os.path.join(self.directory, f))]
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

    def get_full_scale(self):
        """Returns the full scale, which is assumed to be the first lick (index 0)."""
        if self.licks:
            return self.licks[0]
        return None

    def get_scale_by_register(self, register):
        """
        Returns the specific scale part based on the selected register.
        Assumes a fixed order: all (0), low (1), middle (2), high (3).
        """
        register_map = {"low": 1, "middle": 2, "high": 3}
        index = register_map.get(register)
        
        if index is not None and len(self.licks) > index:
            return self.licks[index]
        return None

    def get_combined_scale_for_registers(self, registers):
        """
        Combines multiple scale parts into a single lick object for display.
        """
        combined_data = []
        ordered_registers = [reg for reg in ["low", "middle", "high"] if reg in registers]

        for i, reg in enumerate(ordered_registers):
            scale_part = self.get_scale_by_register(reg)
            if scale_part:
                combined_data.extend(scale_part['lick_data'])
                if i < len(ordered_registers) - 1:
                    combined_data.append({"tab": "rest", "duration": 2})
        
        if not combined_data:
            return None
            
        return {
            "register": ", ".join(ordered_registers),
            "time_signature": "4/4",
            "lick_data": combined_data
        }

    def get_random_lick(self, register="all"):
        """
        Returns a random practice lick and its original index, optionally
        filtered by register.
        """
        # Practice licks start after the scale definitions (all, low, mid, high, and 3 mixed)
        PRACTICE_LICK_START_INDEX = 7
        if len(self.licks) <= PRACTICE_LICK_START_INDEX:
            return None 

        selectable_licks_with_indices = list(enumerate(self.licks))[PRACTICE_LICK_START_INDEX:]
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