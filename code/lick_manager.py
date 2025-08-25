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

    def get_combined_scale_for_registers(self, registers):
        """
        Combines multiple scale parts into a single lick object for display.
        
        Parameters
        ----------
        registers : list
            A list of register names to combine (e.g., ['low', 'middle']).

        Returns
        -------
        dict or None
            A lick object containing the combined lick_data.
        """
        combined_data = []
        for i, reg in enumerate(registers):
            scale_part = self.get_scale_by_register(reg)
            if scale_part:
                combined_data.extend(scale_part['lick_data'])
                # Add a separator rest between scale parts, but not after the last one
                if i < len(registers) - 1:
                    combined_data.append({"tab": "rest", "duration": 4}) # Whole note rest
        
        if not combined_data:
            return None
            
        return {
            "register": ", ".join(registers),
            "time_signature": "4/4", # A nominal time signature for generation
            "lick_data": combined_data
        }


    def get_random_lick(self, register="all"):
        """
        Returns a random practice lick, optionally filtered by register.
        """
        if len(self.licks) <= 3:
            return None 

        selectable_licks = self.licks[3:]
        if not selectable_licks:
            return None

        if register != "all":
            filtered_licks = [lick for lick in selectable_licks if lick.get("register") == register]
            if not filtered_licks:
                return None 
            return random.choice(filtered_licks)
        
        return random.choice(selectable_licks)