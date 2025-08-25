import os
import shutil
from lick_manager import LickManager
from display_tabs import NotationGenerator

# --- Configuration ---
KEYS_TO_GENERATE = ["G", "A", "C", "D"]
OUTPUT_BASE_DIR = os.path.join("licks", "images")

def generate_all_images():
    """
    Loops through all harmonica keys, scale files, and licks to pre-generate
    all the necessary musical score images as PNG files.
    """
    lick_manager = LickManager(licks_directory="licks")
    notation_generator = NotationGenerator()
    
    available_scales = lick_manager.get_available_scales()
    
    if not available_scales:
        print("No scale files found in 'licks' directory. Aborting.")
        return

    print(f"Starting image generation for {len(KEYS_TO_GENERATE)} keys and {len(available_scales)} scales...")
    
    # 1. Loop through each harmonica key
    for key in KEYS_TO_GENERATE:
        print(f"\n--- Processing Key: {key.upper()} Harmonica ---")
        
        # 2. Loop through each scale file (e.g., '1st_position_major')
        for scale_name in available_scales:
            print(f"  -> Generating for scale: {scale_name}")
            
            # Load all the licks for the current scale
            lick_manager.load_licks_for_scale(scale_name)
            
            if not lick_manager.licks:
                print(f"     (Skipping, no licks found in {scale_name}.json)")
                continue
                
            # Create the output directory for this key and scale
            # Example: licks/images/G_harp/1st_position_major/
            output_dir = os.path.join(OUTPUT_BASE_DIR, f"{key.upper()}_harp", scale_name)
            os.makedirs(output_dir, exist_ok=True)
            
            # 3. Loop through each lick in the file
            for i, lick_object in enumerate(lick_manager.licks):
                
                # Determine the correct filename
                if i == 0:
                    filename = "scale_low_register.png"
                elif i == 1:
                    filename = "scale_middle_register.png"
                elif i == 2:
                    filename = "scale_high_register.png"
                else:
                    # Licks are numbered starting from 1 (lick_01, lick_02, etc.)
                    lick_number = i - 2
                    filename = f"lick_{lick_number:02d}.png"

                final_image_path = os.path.join(output_dir, filename)

                # Generate the score image to a temporary path
                temp_image_path = notation_generator.generate_score_image(
                    lick_object['lick_data'],
                    lick_object.get('time_signature', '4/4'),
                    key
                )
                
                # Move the generated image to its final destination
                if temp_image_path and os.path.exists(temp_image_path):
                    shutil.move(temp_image_path, final_image_path)
                    print(f"     ✓ Created {filename}")
                else:
                    print(f"     ✗ Failed to create {filename}")

    print("\n✅ Image generation complete!")


if __name__ == "__main__":
    # Ensure you have music21 and its dependencies (e.g., MuseScore) installed
    # before running this script.
    generate_all_images()