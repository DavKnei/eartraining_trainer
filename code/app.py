import customtkinter
import os
from PIL import Image
from audio_player import AudioPlayer
from lick_manager import LickManager

class EarTrainerApp(customtkinter.CTk):
    """
    The main application class for the Harmonica Ear Trainer.

    This version loads pre-rendered score images for performance and stability.

    Attributes
    ----------
    current_lick : dict or None
        The currently loaded random practice lick object.
    current_lick_index : int or None
        The index of the current lick within its scale file, used for path lookup.
    current_key : str
        The currently selected harmonica key (e.g., "G").
    current_scale : str or None
        The name of the currently loaded scale file (e.g., "1st_position_major").
    current_register : str
        The selected register for filtering licks.
    tabs_visible : bool
        The state tracking whether the practice lick's tabs are currently visible.
    player : AudioPlayer
        An instance of the AudioPlayer for handling sound playback.
    lick_manager : LickManager
        An instance of the LickManager for loading and providing licks.
    """
    def __init__(self):
        """
        Initializes the EarTrainerApp instance.
        """
        super().__init__()

        # ---- App Setup ----
        self.title("Harmonica Ear Trainer")
        self.geometry("650x650")
        self.columnconfigure(0, weight=1)

        # ---- App State ----
        self.current_lick = None
        self.current_lick_index = None
        self.current_key = "G"
        self.current_scale = None
        self.current_register = "low"
        self.tabs_visible = False
        
        # ---- Backend Components ----
        self.player = AudioPlayer()
        self.lick_manager = LickManager(licks_directory="licks")
        if self.lick_manager.available_scales:
            self.current_scale = self.lick_manager.available_scales[0]

        # ---- UI Creation ----
        self._create_widgets()

        # ---- Initial Load ----
        self.player.load_harp_samples(self.current_key)
        self.load_new_lick()

    def _create_widgets(self):
        """
        Creates and arranges all the UI widgets within the main window.
        """
        top_frame = customtkinter.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.columnconfigure((1, 3, 5), weight=1)
        
        customtkinter.CTkLabel(top_frame, text="Harp Key:").grid(row=0, column=0, padx=(10,5), pady=10)
        self.key_menu = customtkinter.CTkOptionMenu(top_frame, values=["G", "A", "C", "D"], command=self.on_control_change)
        self.key_menu.grid(row=0, column=1, padx=(0,10), pady=10, sticky="ew")
        self.key_menu.set(self.current_key)
        
        customtkinter.CTkLabel(top_frame, text="Scale:").grid(row=0, column=2, padx=(10,5), pady=10)
        self.scale_menu = customtkinter.CTkOptionMenu(top_frame, values=self.lick_manager.get_available_scales(), command=self.on_control_change)
        if self.current_scale:
            self.scale_menu.set(self.current_scale)
        self.scale_menu.grid(row=0, column=3, padx=(0,10), pady=10, sticky="ew")

        customtkinter.CTkLabel(top_frame, text="Register:").grid(row=0, column=4, padx=(10,5), pady=10)
        available_registers = ["all", "low", "middle", "high", "mixed"]
        self.register_menu = customtkinter.CTkOptionMenu(top_frame, values=available_registers, command=self.on_control_change)
        self.register_menu.grid(row=0, column=5, padx=(0,10), pady=10, sticky="ew")
        self.register_menu.set(self.current_register)
        
        # This frame will contain the reference scale label
        self.scale_display_frame = customtkinter.CTkFrame(self)
        self.scale_display_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.scale_display_frame.columnconfigure(0, weight=1)
        customtkinter.CTkLabel(self.scale_display_frame, text="Reference Scale", font=("Arial", 14)).grid(row=0, column=0, pady=(5,0))
        # The label itself is now created/destroyed in the update method

        # This frame will contain the practice lick label
        self.lick_frame = customtkinter.CTkFrame(self)
        self.lick_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.lick_frame.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.lick_info_label = customtkinter.CTkLabel(self.lick_frame, text="Practice Lick", font=("Arial", 14))
        self.lick_info_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        # The label itself is now created/destroyed in the update method

        controls_frame = customtkinter.CTkFrame(self)
        controls_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        controls_frame.columnconfigure((0, 1, 2), weight=1)
        self.new_lick_button = customtkinter.CTkButton(controls_frame, text="New Lick", command=self.load_new_lick)
        self.new_lick_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        self.play_button = customtkinter.CTkButton(controls_frame, text="Play Lick", command=self.play_current_lick)
        self.play_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.toggle_tabs_button = customtkinter.CTkButton(controls_frame, text="Show Tabs", command=self.toggle_tabs_visibility)
        self.toggle_tabs_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        
        bpm_frame = customtkinter.CTkFrame(self)
        bpm_frame.grid(row=4, column=0, padx=10, pady=(0,10), sticky="ew")
        bpm_frame.columnconfigure(1, weight=1)
        self.bpm_label = customtkinter.CTkLabel(bpm_frame, text="BPM: 120")
        self.bpm_label.grid(row=0, column=0, padx=10, pady=10)
        self.bpm_slider = customtkinter.CTkSlider(bpm_frame, from_=60, to=240, number_of_steps=180, command=self.update_bpm_label)
        self.bpm_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.bpm_slider.set(120)

    def on_control_change(self, value: str):
        """
        Handles events from the top control dropdowns (Key, Scale, Register).
        """
        key_changed = self.current_key != self.key_menu.get()
        scale_changed = self.current_scale != self.scale_menu.get()
        register_changed = self.current_register != self.register_menu.get()

        self.current_key = self.key_menu.get()
        self.current_scale = self.scale_menu.get()
        self.current_register = self.register_menu.get()
        
        if key_changed:
             self.player.load_harp_samples(self.current_key)
             
        if scale_changed:
            self.lick_manager.load_licks_for_scale(self.current_scale)

        if scale_changed or register_changed:
            self.load_new_lick()
        else: 
            self._update_scale_display()
            self._update_lick_display()

    def _update_scale_display(self):
        """
        Loads and displays the pre-rendered reference scale image by
        destroying and recreating the label.
        """
        # FIX: Destroy the old label if it exists to prevent overlap/memory issues
        if hasattr(self, "scale_notation_label"):
            self.scale_notation_label.destroy()

        # Recreate the label in its parent frame
        self.scale_notation_label = customtkinter.CTkLabel(self.scale_display_frame, text="")
        self.scale_notation_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        register_to_display = self.current_register if self.current_register not in ["all", "mixed"] else "low"
        filename = f"scale_{register_to_display}_register.png"
        image_path = os.path.join("licks", "images", f"{self.current_key.upper()}_harp", self.current_scale, filename)
        
        if os.path.exists(image_path):
            image_obj = customtkinter.CTkImage(light_image=Image.open(image_path), size=(600, 120))
            self.scale_notation_label.configure(image=image_obj)
            self.scale_notation_label.image = image_obj
        else:
            self.scale_notation_label.configure(text="Reference image not found.")
            
    def load_new_lick(self):
        """
        Fetches a new random lick and its index, then updates the UI.
        """
        lick_info = self.lick_manager.get_random_lick(register=self.current_register)
        if lick_info:
            self.current_lick, self.current_lick_index = lick_info
        else:
            self.current_lick, self.current_lick_index = None, None
            
        self.tabs_visible = False
        self._update_scale_display()
        self._update_lick_display()

    def _update_lick_display(self):
        """
        Updates the lower practice lick display by destroying and
        recreating the label.
        """
        # FIX: Destroy the old label if it exists to prevent overlap/memory issues
        if hasattr(self, "lick_notation_label"):
            self.lick_notation_label.destroy()

        # Recreate the label in its parent frame
        self.lick_notation_label = customtkinter.CTkLabel(self.lick_frame, text="")
        self.lick_notation_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        if self.current_lick:
            self.lick_info_label.configure(text=f"Practice Lick (Register: {self.current_lick.get('register', 'N/A')})")
            
            if self.tabs_visible:
                lick_number = self.current_lick_index - 2
                filename = f"lick_{lick_number:02d}.png"
                image_path = os.path.join("licks", "images", f"{self.current_key.upper()}_harp", self.current_scale, filename)

                if os.path.exists(image_path):
                    lick_image_obj = customtkinter.CTkImage(light_image=Image.open(image_path), size=(600, 120))
                    self.lick_notation_label.configure(image=lick_image_obj)
                    self.lick_notation_label.image = lick_image_obj
                else:
                    self.lick_notation_label.configure(text="Lick image not found.")
                self.toggle_tabs_button.configure(text="Hide Tabs")
            else:
                self.lick_notation_label.configure(text="???", font=("Arial", 28, "bold"))
                self.toggle_tabs_button.configure(text="Show Tabs")
        else:
            self.lick_info_label.configure(text="Practice Lick")
            self.lick_notation_label.configure(text=f"No '{self.current_register}' licks in file.", font=("Arial", 20))

    def play_current_lick(self):
        """
        Plays the audio of the currently loaded practice lick.
        """
        if self.current_lick:
            self.player.play_lick(self.current_lick['lick_data'], self.bpm_slider.get())

    def toggle_tabs_visibility(self):
        """
        Toggles the visibility state of the practice lick's score.
        """
        self.tabs_visible = not self.tabs_visible
        self._update_lick_display()
    
    def update_bpm_label(self, value: float):
        """
        Updates the BPM label as the slider is moved.
        """
        self.bpm_label.configure(text=f"BPM: {int(value)}")


if __name__ == "__main__":
    # customtkinter.set_appearance_mode("System")
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("blue")

    app = EarTrainerApp()
    app.mainloop()