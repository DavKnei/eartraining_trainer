import json
import random

class LickManager:
    """
    Handles loading and providing licks from a JSON data source.
    """
    def __init__(self, licks_filepath="licks/example_licks.json"):
        self.filepath = licks_filepath
        self.licks = self._load_licks()
        if self.licks:
            print(f"LickManager initialized. Loaded {len(self.licks)} licks from {self.filepath}")

    def _load_licks(self):
        """
        Loads the lick data from the specified JSON file.
        """
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                return data.get("licks", []) # Safely get the list of licks
        except FileNotFoundError:
            print(f"ERROR: Licks file not found at {self.filepath}")
            return []
        except json.JSONDecodeError:
            print(f"ERROR: Could not decode JSON from {self.filepath}. Check for syntax errors.")
            return []

    def get_random_lick(self):
        """
        Returns a single random lick from the loaded list.
        """
        if not self.licks:
            print("Warning: No licks loaded to choose from.")
            return None
        return random.choice(self.licks)

    def get_all_licks(self):
        """
        Returns the entire list of loaded licks.
        """
        return self.licks

# --- Example of how to use this class ---
if __name__ == "__main__":
    # This is a test block to make sure our manager works.
    
    licks_file_path = "licks/example_licks.json" 

    # 2. Create an instance of the manager
    manager = LickManager(licks_filepath=licks_file_path)

    # 3. Check if licks were loaded
    if manager.licks:
        # 4. Get a random lick
        random_lick = manager.get_random_lick()
        
        print("\n--- Testing get_random_lick() ---")
        if random_lick:
            print(f"Got random lick in register: {random_lick.get('register', 'N/A')}")
            # Print the first few notes for confirmation
            print(f"Lick data starts with: {random_lick.get('lick_data', [])[:3]}")

        # 5. Get the total number of licks
        all_licks = manager.get_all_licks()
        print(f"\nTotal number of licks available: {len(all_licks)}")