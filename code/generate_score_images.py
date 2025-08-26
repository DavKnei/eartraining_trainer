import os
import shutil
import multiprocessing
from lick_manager import LickManager
from display_tabs import NotationGenerator

# --- Configuration ---
KEYS_TO_GENERATE = ["G", "A", "C", "D"]
OUTPUT_BASE_DIR = os.path.join("licks", "images")


def generate_images_for_key(key):
    """
    Generates all score images for a single, specified harmonica key.
    This function is designed to be run as a separate process.
    """
    print(f"Starting process for Key: {key.upper()} Harmonica...")

    lick_manager = LickManager(licks_directory="licks")
    notation_generator = NotationGenerator()

    available_scales = lick_manager.get_available_scales()

    for scale_name in available_scales:
        print(f"  [{key.upper()}] Generating for scale: {scale_name}")

        lick_manager.load_licks_for_scale(scale_name)

        if not lick_manager.licks:
            continue

        output_dir = os.path.join(OUTPUT_BASE_DIR, f"{key.upper()}_harp", scale_name)
        os.makedirs(output_dir, exist_ok=True)

        # Generate images for each lick in the JSON file
        for lick_object in lick_manager.licks:
            lick_name = lick_object.get("name")
            if not lick_name:
                print(
                    f"     ✗ [{key.upper()}] Lick in {scale_name} is missing a 'name'. Skipping."
                )
                continue

            filename = f"{lick_name}.png"
            final_image_path = os.path.join(output_dir, filename)

            temp_image_path = notation_generator.generate_score_image(
                lick_object["lick_data"], lick_object.get("time_signature", "4/4"), key
            )

            if temp_image_path and os.path.exists(temp_image_path):
                shutil.move(temp_image_path, final_image_path)
                print(f"     ✓ Created {filename}")
            else:
                print(f"     ✗ [{key.upper()}] Failed to create {filename}")

    print(f"Finished process for Key: {key.upper()} Harmonica.")


if __name__ == "__main__":

    print(f"Starting parallel image generation for keys: {', '.join(KEYS_TO_GENERATE)}")

    with multiprocessing.Pool() as pool:
        pool.map(generate_images_for_key, KEYS_TO_GENERATE)

    print("\n✅ All parallel processes finished. Image generation complete!")
