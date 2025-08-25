import customtkinter
from audio_player import AudioPlayer
from lick_manager import LickManager

class EarTrainerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # ---- App Setup ----
        self.title("Harmonica Ear Trainer")
        self.geometry("450x380") # Increased height slightly for the new button
        self.grid_columnconfigure(0, weight=1)

        # ---- App State ----
        self.current_lick = None
        self.current_key = "G"
        self.tabs_visible = False  # NEW: State to track tab visibility, default is False (hidden)

        # ---- Backend Components ----
        self.player = AudioPlayer()
        self.lick_manager = LickManager(licks_filepath="licks/example_licks.json")

        # ---- UI Creation ----
        self._create_widgets()

        # ---- Initial Load ----
        self.player.load_harp_samples(self.current_key)
        self.load_new_lick()

    def _create_widgets(self):
        """Creates and places all the UI widgets in the window."""

        # -- Top Frame for Key Selection --
        top_frame = customtkinter.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)
        
        key_label = customtkinter.CTkLabel(top_frame, text="Harp Key:")
        key_label.grid(row=0, column=0, padx=10, pady=10)

        available_keys = ["G", "A", "C", "D"]
        self.key_menu = customtkinter.CTkOptionMenu(top_frame, values=available_keys, command=self.on_key_change)
        self.key_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.key_menu.set(self.current_key)
        
        # -- Lick Display Frame --
        display_frame = customtkinter.CTkFrame(self)
        display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)

        self.lick_info_label = customtkinter.CTkLabel(display_frame, text="Register: ... | Time: ...", font=("Arial", 14))
        self.lick_info_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        self.lick_tabs_label = customtkinter.CTkLabel(display_frame, text="???", font=("Arial", 28, "bold"))
        self.lick_tabs_label.grid(row=1, column=0, padx=10, pady=5)
        
        # -- Controls Frame --
        controls_frame = customtkinter.CTkFrame(self)
        controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        # MODIFIED: Configure 3 columns to be of equal weight
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.new_lick_button = customtkinter.CTkButton(controls_frame, text="New Lick", command=self.load_new_lick)
        self.new_lick_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        self.play_button = customtkinter.CTkButton(controls_frame, text="Play Lick", command=self.play_current_lick)
        self.play_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # NEW: Show/Hide tabs button
        self.toggle_tabs_button = customtkinter.CTkButton(controls_frame, text="Show Tabs", command=self.toggle_tabs_visibility)
        self.toggle_tabs_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        # -- BPM Control --
        bpm_frame = customtkinter.CTkFrame(self)
        bpm_frame.grid(row=3, column=0, padx=10, pady=(0,10), sticky="ew")
        bpm_frame.grid_columnconfigure(1, weight=1)

        self.bpm_label = customtkinter.CTkLabel(bpm_frame, text="BPM: 120")
        self.bpm_label.grid(row=0, column=0, padx=10, pady=10)

        self.bpm_slider = customtkinter.CTkSlider(bpm_frame, from_=60, to=240, number_of_steps=180, command=self.update_bpm_label)
        self.bpm_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.bpm_slider.set(120)

    # --- UI COMMANDS AND LOGIC ---

    def on_key_change(self, selected_key: str):
        print(f"Changing key to {selected_key}")
        self.current_key = selected_key
        self.player.load_harp_samples(self.current_key)

    def load_new_lick(self):
        """Fetches a new random lick and updates the UI."""
        self.current_lick = self.lick_manager.get_random_lick()
        if self.current_lick:
            info_text = f"Register: {self.current_lick.get('register', 'N/A')} | Time: {self.current_lick.get('time_signature', 'N/A')}"
            self.lick_info_label.configure(text=info_text)
            # MODIFIED: Call a helper to update the display according to the current visibility state
            self._update_lick_display()

    def play_current_lick(self):
        if self.current_lick:
            bpm = self.bpm_slider.get()
            self.player.play_lick(self.current_lick['lick_data'], bpm)
        else:
            print("No lick loaded to play.")
            
    def update_bpm_label(self, value):
        self.bpm_label.configure(text=f"BPM: {int(value)}")

    # NEW: Method to toggle tab visibility
    def toggle_tabs_visibility(self):
        """Flips the visibility state and updates the UI."""
        self.tabs_visible = not self.tabs_visible
        self._update_lick_display()

    # NEW: Helper method to centralize display logic
    def _update_lick_display(self):
        """Updates the lick tab label and button text based on visibility state."""
        if not self.current_lick:
            return

        if self.tabs_visible:
            # State is VISIBLE: show the tabs and set button text to "Hide"
            tabs_string = " ".join([note['tab'] for note in self.current_lick['lick_data']])
            self.lick_tabs_label.configure(text=tabs_string)
            self.toggle_tabs_button.configure(text="Hide Tabs")
        else:
            # State is HIDDEN: show question marks and set button text to "Show"
            self.lick_tabs_label.configure(text="???")
            self.toggle_tabs_button.configure(text="Show Tabs")


if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    
    app = EarTrainerApp()
    app.mainloop()