import os
import shutil
import multiprocessing
from lick_manager import LickManager
from display_tabs import NotationGenerator

# --- Configuration ---
KEYS_TO_GENERATE = ["G", "A", "C", "D"]
OUTPUT_BASE_DIR = os.path.join("licks", "images")

#  Contains all the logic for a single key.
def generate_images_for_key(key):
    """
    Generates all score images for a single, specified harmonica key.
    This function is designed to be run as a separate process.

    Parameters
    ----------
    key : str
        The harmonica key to process (e.g., "G").
    """
    print(f"Starting process for Key: {key.upper()} Harmonica...")
    
    # Each process needs its own instances of these classes.
    lick_manager = LickManager(licks_directory="licks")
    notation_generator = NotationGenerator()
    
    available_scales = lick_manager.get_available_scales()

    # Loop through each scale file (e.g., '1st_position_major')
    for scale_name in available_scales:
        print(f"  [{key.upper()}] Generating for scale: {scale_name}")
        
        lick_manager.load_licks_for_scale(scale_name)
        
        if not lick_manager.licks:
            continue
            
        output_dir = os.path.join(OUTPUT_BASE_DIR, f"{key.upper()}_harp", scale_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Loop through each lick in the file
        for i, lick_object in enumerate(lick_manager.licks):
            if i == 0:
                filename = "scale_low_register.png"
            elif i == 1:
                filename = "scale_middle_register.png"
            elif i == 2:
                filename = "scale_high_register.png"
            else:
                lick_number = i - 2
                filename = f"lick_{lick_number:02d}.png"

            final_image_path = os.path.join(output_dir, filename)

            temp_image_path = notation_generator.generate_score_image(
                lick_object['lick_data'],
                lick_object.get('time_signature', '4/4'),
                key
            )
            
            if temp_image_path and os.path.exists(temp_image_path):
                shutil.move(temp_image_path, final_image_path)
            else:
                print(f"     ✗ [{key.upper()}] Failed to create {filename}")
                
    print(f"Finished process for Key: {key.upper()} Harmonica.")


if __name__ == "__main__":
    
    print(f"Starting parallel image generation for keys: {', '.join(KEYS_TO_GENERATE)}")
    
    # Create a pool of worker processes. By default, this uses all available CPU cores.
    with multiprocessing.Pool() as pool:
        # The map function takes the worker function and the list of keys,
        # and distributes the work among the processes in the pool.
        pool.map(generate_images_for_key, KEYS_TO_GENERATE)
        
    print("\n✅ All parallel processes finished. Image generation complete!")