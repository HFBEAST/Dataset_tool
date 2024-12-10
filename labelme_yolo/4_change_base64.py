import os
import base64
import json

def tack_base64(img_path, json_path, new_img_name):
    # Read and encode the image in base64
    with open(img_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    # Read the existing JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Update the 'imageData' and 'imagePath' in JSON
    json_data['imageData'] = img_base64
    json_data['imagePath'] = new_img_name

    return json_data

def change_base64(input_path, img_extensions=None):
    if img_extensions is None:
        img_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.svg', '.ico']

    for filename in os.listdir(input_path):
        file_root, ext = os.path.splitext(filename)

        if ext.lower() in img_extensions:
            img_path = os.path.join(input_path, filename)
            json_path = os.path.join(input_path, file_root + '.json')

            if os.path.exists(json_path):
                # Define new filenames with '_1' appended
                new_file_root = f"{file_root}_1"
                new_img_name = new_file_root + ext
                new_json_name = new_file_root + '.json'
                new_img_path = os.path.join(input_path, new_img_name)
                new_json_path = os.path.join(input_path, new_json_name)

                # Update JSON data with new image data and image path
                updated_json = tack_base64(img_path, json_path, new_img_name)

                # Write the updated JSON to the new JSON file
                with open(new_json_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_json, f, indent=4, ensure_ascii=False)

                # Rename the image file to the new image name
                os.rename(img_path, new_img_path)

                # Optionally, remove the old JSON file if desired
                os.remove(json_path)

                print(f"Successfully updated and renamed to {new_file_root} with image data.")
            else:
                print(f"Warning: JSON file {file_root}.json does not exist for image {filename}.")

if __name__ == '__main__':
    input_path = r'E:\SUBPJ\GIO\aiba\dataset\pose\0_sum_1750_aug'
    change_base64(input_path)
