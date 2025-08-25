import customtkinter
from PIL import Image
from audio_player import AudioPlayer
from lick_manager import LickManager
from display_tabs import NotationGenerator

class EarTrainerApp(customtkinter.CTk):
    """
    The main application class for the Harmonica Ear Trainer.

    This class initializes the main window, manages the application's state,
    creates the user interface, and connects UI events to the backend logic
    provided by AudioPlayer, LickManager, and NotationGenerator.

    Attributes
    ----------
    current_lick : dict or None
        The currently loaded lick data object.
    current_key : str
        The currently selected harmonica key (e.g., "G").
    tabs_visible : bool
        The state tracking whether the lick's tabs are currently visible.
    score_image_object : customtkinter.CTkImage or None
        A persistent reference to the score image object to prevent garbage collection.
    player : AudioPlayer
        An instance of the AudioPlayer for handling sound playback.
    lick_manager : LickManager
        An instance of the LickManager for loading and providing licks.
    notation_generator : NotationGenerator
        An instance for generating musical score images from lick data.
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
        self.geometry("550x450")
        self.grid_columnconfigure(0, weight=1)

        # ---- App State ----
        self.current_lick = None
        self.current_key = "G"
        self.tabs_visible = False
        self.score_image_object = None  # Attribute to hold the image reference

        # ---- Backend Components ----
        self.player = AudioPlayer()
        self.lick_manager = LickManager(licks_filepath="licks/example_licks.json")
        self.notation_generator = NotationGenerator()

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

        # -- Lick Display Frame for Score --
        display_frame = customtkinter.CTkFrame(self)
        display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.lick_info_label = customtkinter.CTkLabel(display_frame, text="Register: ... | Time: ...", font=("Arial", 14))
        self.lick_info_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        # This single label now handles both the image and the "???" placeholder
        self.score_image_label = customtkinter.CTkLabel(display_frame, text="???", font=("Arial", 28, "bold"))
        self.score_image_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

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
        """
        self.current_lick = self.lick_manager.get_random_lick()
        if self.current_lick:
            info_text = f"Register: {self.current_lick.get('register', 'N/A')} | Time: {self.current_lick.get('time_signature', 'N/A')}"
            self.lick_info_label.configure(text=info_text)
            self._update_lick_display()

    def play_current_lick(self):
        """
        Plays the audio of the currently loaded lick.
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
        Toggles the visibility state of the lick's score.
        """
        self.tabs_visible = not self.tabs_visible
        self._update_lick_display()

    def _update_lick_display(self):
        """
        Updates the display area to show the score or a placeholder.

        If `tabs_visible` is True, it generates and displays the score image.
        If False, it clears the image and shows a "???" placeholder.
        """
        if not self.current_lick:
            return

        if self.tabs_visible:
            # Generate the score image
            image_path = self.notation_generator.generate_score_image(
                self.current_lick['lick_data'],
                self.current_lick.get('time_signature', '4/4'),
                self.current_key
            )
            
            # Display the score image
            if image_path:
                try:
                    # Store the image object in the instance attribute to prevent garbage collection
                    self.score_image_object = customtkinter.CTkImage(light_image=Image.open(image_path), size=(500, 120))
                    # Configure the label to show the image and have no text
                    self.score_image_label.configure(image=self.score_image_object, text="")
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.score_image_label.configure(image=None, text="Error generating score.")
            else:
                self.score_image_label.configure(image=None, text="Error generating score.")
            
            self.toggle_tabs_button.configure(text="Hide Tabs")
        else:
            # Clear the image and set the placeholder text on the same label
            self.score_image_label.configure(image=None, text="???", font=("Arial", 28, "bold"))
            self.toggle_tabs_button.configure(text="Show Tabs")


if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    app = EarTrainerApp()
    app.mainloop()