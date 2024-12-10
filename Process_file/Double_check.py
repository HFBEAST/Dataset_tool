import os
import json
from shutil import move
from collections import defaultdict


def rename_duplicates(root_dir, target_dir):
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)
    # Tracker for already processed file names
    file_tracker = defaultdict(int)
    # Supported file extensions
    supported_extensions = {'.jpg', '.jpeg', '.png', '.json'}

    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(subdir, file)
            # Check if the file extension is in the supported list
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_extensions:
                new_file_name = file
                # Check if the file already exists in the target directory
                while os.path.exists(os.path.join(target_dir, new_file_name)):
                    # If the file exists, prepend 'x' to the file name
                    new_file_name = 'x' + new_file_name
                # Move and rename the file
                new_file_path = os.path.join(target_dir, new_file_name)
                move(file_path, new_file_path)
                print(f"Moved {file_path} to {new_file_path}")

                # If the file is a json, update its "imagePath" field
                if ext == '.json':
                    update_json_imagepath(new_file_path, new_file_name)


def update_json_imagepath(json_file_path, new_image_file_name):
    """Update the 'imagePath' field in the json file with the new image file name."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update the 'imagePath' field with the new image file name
    data['imagePath'] = new_image_file_name.replace('.json', '.jpg')

    # Save the updated json back to the file
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Updated {json_file_path} with imagePath: {data['imagePath']}")


# Specify the root and target directories
root_directory = r'D:\23333\archive_dataset'  # Change to your root directory path
target_directory = r'H:\DATASET\horses\sum'  # Change to your target directory path

# Call the function
rename_duplicates(root_directory, target_directory)
