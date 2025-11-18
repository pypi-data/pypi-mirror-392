# renamer.py
import os
import shutil
from .classifier import classify_image, load_model
from .utils import get_image_files, create_output_folder

def rename_images(input_folder, output_folder):
    """
    Rename all images in input_folder based on AI classification.
    Format: label(confidence%)(counter).ext
    """
    model = load_model()
    create_output_folder(output_folder)
    image_files = get_image_files(input_folder)

    counter_dict = {}  # for duplicates

    for img_file in image_files:
        img_path = os.path.join(input_folder, img_file)
        try:
            label, confidence = classify_image(img_path, model)
            confidence_percent = f"{confidence*100:.2f}%"

            # the update of counter (for duplicates)
            key = f"{label}({confidence_percent})"
            if key not in counter_dict:
                counter_dict[key] = 1
            else:
                counter_dict[key] += 1
            count = counter_dict[key]

            # Get file extension
            ext = os.path.splitext(img_file)[1]
            new_name = f"{label}({confidence_percent})({count}){ext}"
            new_path = os.path.join(output_folder, new_name)

            # Copy original image to new path with new name
            shutil.copy2(img_path, new_path)
            print(f"Renamed {img_file} → {new_name}")

        except Exception as e:
            print(f"[Warning] Could not process {img_file}: {e}")
