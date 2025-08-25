import customtkinter
from audio_player import AudioPlayer
from lick_manager import LickManager

class EarTrainerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # ---- App Setup ----
        self.title("Harmonica Ear Trainer")
        self.geometry("450x350")
        self.grid_columnconfigure(0, weight=1)

        # ---- App State ----
        self.current_lick = None
        self.current_key = "G" # Default key

        # ---- Backend Components ----
        self.player = AudioPlayer()
        self.lick_manager = LickManager(licks_filepath="licks/example_licks.json")

        # ---- UI Creation ----
        self._create_widgets()

        # ---- Initial Load ----
        # Load samples for the default key at startup
        self.player.load_harp_samples(self.current_key)
        # Load the first lick
        self.load_new_lick()

    def _create_widgets(self):
        """Creates and places all the UI widgets in the window."""

        # -- Top Frame for Key Selection --
        top_frame = customtkinter.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)
        
        key_label = customtkinter.CTkLabel(top_frame, text="Harp Key:")
        key_label.grid(row=0, column=0, padx=10, pady=10)

        # Assumes you have samples for these keys
        available_keys = ["G", "A", "C", "D"]
        self.key_menu = customtkinter.CTkOptionMenu(top_frame, values=available_keys, command=self.on_key_change)
        self.key_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.key_menu.set(self.current_key)
        
        # -- Lick Display Frame --
        display_frame = customtkinter.CTkFrame(self)
        display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)

        self.lick_info_label = customtkinter.CTkLabel(display_frame, text="Register: Middle | Time: 4/4", font=("Arial", 14))
        self.lick_info_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        self.lick_tabs_label = customtkinter.CTkLabel(display_frame, text="-2 -3' 4...", font=("Arial", 28, "bold"))
        self.lick_tabs_label.grid(row=1, column=0, padx=10, pady=5)
        
        # -- Controls Frame --
        controls_frame = customtkinter.CTkFrame(self)
        controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1) # Allow button to expand
        controls_frame.grid_columnconfigure(1, weight=1) # Allow button to expand

        self.new_lick_button = customtkinter.CTkButton(controls_frame, text="New Lick", command=self.load_new_lick)
        self.new_lick_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        self.play_button = customtkinter.CTkButton(controls_frame, text="Play Lick", command=self.play_current_lick)
        self.play_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # -- BPM Control --
        bpm_frame = customtkinter.CTkFrame(self)
        bpm_frame.grid(row=3, column=0, padx=10, pady=(0,10), sticky="ew")
        bpm_frame.grid_columnconfigure(1, weight=1)

        self.bpm_label = customtkinter.CTkLabel(bpm_frame, text="BPM: 120")
        self.bpm_label.grid(row=0, column=0, padx=10, pady=10)

        self.bpm_slider = customtkinter.CTkSlider(bpm_frame, from_=60, to=240, number_of_steps=180, command=self.update_bpm_label)
        self.bpm_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.bpm_slider.set(120)


    def on_key_change(self, selected_key: str):
        """Called when the user selects a new harmonica key."""
        print(f"Changing key to {selected_key}")
        self.current_key = selected_key
        # Load the audio samples for the newly selected key
        self.player.load_harp_samples(self.current_key)

    def load_new_lick(self):
        """Fetches a new random lick and updates the display."""
        self.current_lick = self.lick_manager.get_random_lick()
        if self.current_lick:
            # Format the tab data into a readable string
            tabs_string = " ".join([note['tab'] for note in self.current_lick['lick_data']])
            # Update the UI labels
            self.lick_tabs_label.configure(text=tabs_string)
            info_text = f"Register: {self.current_lick.get('register', 'N/A')} | Time: {self.current_lick.get('time_signature', 'N/A')}"
            self.lick_info_label.configure(text=info_text)

    def play_current_lick(self):
        """Plays the currently loaded lick using the audio player."""
        if self.current_lick:
            bpm = self.bpm_slider.get()
            self.player.play_lick(self.current_lick['lick_data'], bpm)
        else:
            print("No lick loaded to play.")
            
    def update_bpm_label(self, value):
        """Updates the BPM label as the slider is moved."""
        self.bpm_label.configure(text=f"BPM: {int(value)}")


if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"
    
    app = EarTrainerApp()
    app.mainloop()