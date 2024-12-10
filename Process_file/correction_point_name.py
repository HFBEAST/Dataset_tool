import os
import json
import argparse
from collections import defaultdict


def correct_labels_in_json(json_data, corrections):
    """
    Correct label names in JSON data based on the corrections mapping.

    Args:
        json_data (dict): Loaded JSON data.
        corrections (dict): Mapping dictionary from incorrect labels to correct labels.

    Returns:
        list: Records all modified (old_label, new_label) tuples.
    """
    modified_labels = []

    # Ensure the 'shapes' key exists and is a list
    if 'shapes' in json_data and isinstance(json_data['shapes'], list):
        for shape in json_data['shapes']:
            if 'label' in shape:
                original_label = shape['label']
                if original_label in corrections:
                    new_label = corrections[original_label]
                    shape['label'] = new_label
                    modified_labels.append((original_label, new_label))
    return modified_labels


def process_json_file(file_path, corrections):
    """
    Process a single JSON file, correct label names, and return modification records.

    Args:
        file_path (str): Path to the JSON file.
        corrections (dict): Mapping dictionary from incorrect labels to correct labels.

    Returns:
        list: Records all modified (old_label, new_label) tuples.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse JSON file {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Warning: Error reading file {file_path}: {e}")
        return []

    modified_labels = correct_labels_in_json(json_data, corrections)

    if modified_labels:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error: Unable to write modified JSON file {file_path}: {e}")
            return []

    return modified_labels


def traverse_and_modify(root_dir, corrections):
    """
    Traverse all JSON files in the root directory and its subdirectories to correct label names.

    Args:
        root_dir (str): Path to the root directory.
        corrections (dict): Mapping dictionary from incorrect labels to correct labels.

    Returns:
        dict: Records all modified files and their specific modifications.
    """
    modified_files = defaultdict(list)

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.json'):
                file_path = os.path.join(dirpath, filename)
                modifications = process_json_file(file_path, corrections)
                if modifications:
                    modified_files[file_path].extend(modifications)

    return modified_files


def main(root_dir):
    # Define label correction mapping
    corrections = {
        "L_F_knee": "L_F_Knee",
        "L_B_knee": "L_B_Knee",
        "R_F_knee": "R_B_Knee",
        "R_B_knee": "R_F_Knee"
    }

    if not os.path.isdir(root_dir):
        print(f"Error: The specified path '{root_dir}' is not a valid directory.")
        return

    print(f"Starting processing directory: {root_dir}\n")

    modified_files = traverse_and_modify(root_dir, corrections)

    if modified_files:
        print("\nProcessing complete! The following files were modified with their changes:\n")
        for file_path, changes in modified_files.items():
            print(f"File: {file_path}")
            for old_label, new_label in changes:
                print(f"  - Label corrected: '{old_label}' → '{new_label}'")
            print()  # Add a blank line for readability
        print(f"Total of {len(modified_files)} files were modified.")
    else:
        print("No labels needed to be modified.")


if __name__ == "__main__":
    root_dir = r"E:\SUBPJ\GIO\aiba\dataset\pose\0_horse_3500_labelme_aug+org"
    main(root_dir)
