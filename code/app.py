import customtkinter
from audio_player import AudioPlayer
from lick_manager import LickManager

class EarTrainerApp(customtkinter.CTk):
    """
    The main application class for the Harmonica Ear Trainer.

    This class initializes the main window, manages the application's state,
    creates the user interface, and connects UI events to the backend logic
    provided by AudioPlayer and LickManager.

    Attributes
    ----------
    current_lick : dict or None
        The currently loaded lick data object.
    current_key : str
        The currently selected harmonica key (e.g., "G").
    tabs_visible : bool
        The state tracking whether the lick's tabs are currently visible.
    player : AudioPlayer
        An instance of the AudioPlayer for handling sound playback.
    lick_manager : LickManager
        An instance of the LickManager for loading and providing licks.
    """
    def __init__(self):
        """
        Initializes the EarTrainerApp instance.

        Sets up the main window, initializes state variables, instantiates
        backend components, and builds the user interface.
        """
        super().__init__()

        # ---- App Setup ----
        self.title("Harmonica Ear Trainer")
        self.geometry("450x380")
        self.grid_columnconfigure(0, weight=1)

        # ---- App State ----
        self.current_lick = None
        self.current_key = "G"
        self.tabs_visible = False

        # ---- Backend Components ----
        self.player = AudioPlayer()
        self.lick_manager = LickManager(licks_filepath="licks/example_licks.json")

        # ---- UI Creation ----
        self._create_widgets()

        # ---- Initial Load ----
        self.player.load_harp_samples(self.current_key)
        self.load_new_lick()

    def _create_widgets(self):
        """
        Creates and arranges all the UI widgets within the main window.

        This method is responsible for building the entire graphical user
        interface, including frames, labels, buttons, and sliders.
        """
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
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.new_lick_button = customtkinter.CTkButton(controls_frame, text="New Lick", command=self.load_new_lick)
        self.new_lick_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        self.play_button = customtkinter.CTkButton(controls_frame, text="Play Lick", command=self.play_current_lick)
        self.play_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

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

    def on_key_change(self, selected_key: str):
        """
        Handles the event when a new harmonica key is selected.

        This callback function is triggered by the key selection dropdown menu.
        It updates the application's current key state and instructs the
        AudioPlayer to load the corresponding audio samples.

        Parameters
        ----------
        selected_key : str
            The new key selected by the user from the dropdown (e.g., "G").
        """
        print(f"Changing key to {selected_key}")
        self.current_key = selected_key
        self.player.load_harp_samples(self.current_key)

    def load_new_lick(self):
        """
        Fetches a new random lick and updates the user interface.

        This method gets a random lick from the LickManager, updates the
        application's `current_lick` state, and then calls the display
        update function to refresh the UI with the new lick's information.
        """
        self.current_lick = self.lick_manager.get_random_lick()
        if self.current_lick:
            info_text = f"Register: {self.current_lick.get('register', 'N/A')} | Time: {self.current_lick.get('time_signature', 'N/A')}"
            self.lick_info_label.configure(text=info_text)
            self._update_lick_display()

    def play_current_lick(self):
        """
        Plays the audio of the currently loaded lick.

        Retrieves the current BPM from the slider and passes the lick data
        to the AudioPlayer to be played.
        """
        if self.current_lick:
            bpm = self.bpm_slider.get()
            self.player.play_lick(self.current_lick['lick_data'], bpm)
        else:
            print("No lick loaded to play.")

    def update_bpm_label(self, value: float):
        """
        Updates the BPM label in real-time as the slider is moved.

        Parameters
        ----------
        value : float
            The current numerical value from the BPM slider.
        """
        self.bpm_label.configure(text=f"BPM: {int(value)}")

    def toggle_tabs_visibility(self):
        """
        Toggles the visibility state of the lick's tabs.

        This method inverts the `tabs_visible` boolean state and then
        calls the display update function to reflect the change in the UI.
        """
        self.tabs_visible = not self.tabs_visible
        self._update_lick_display()

    def _update_lick_display(self):
        """
        Updates the lick display area based on the current visibility state.

        If `tabs_visible` is True, it shows the formatted tabs. If False,
        it hides them and displays a placeholder. It also updates the text
        of the toggle button accordingly.
        """
        if not self.current_lick:
            return

        if self.tabs_visible:
            tabs_string = " ".join([note['tab'] for note in self.current_lick['lick_data']])
            # This is a placeholder for the formatted tabs from your previous version.
            # In the full version, this would also handle the score image generation and display.
            self.lick_tabs_label.configure(text=tabs_string)
            self.toggle_tabs_button.configure(text="Hide Tabs")
        else:
            self.lick_tabs_label.configure(text="???")
            self.toggle_tabs_button.configure(text="Show Tabs")


if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    app = EarTrainerApp()
    app.mainloop()