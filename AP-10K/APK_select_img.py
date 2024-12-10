import json
import os
import shutil

def copy_images_from_json_folder(json_folder, image_source_folder, image_target_folder):
    # 获取所有 JSON 文件
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    image_names = set()

    # 遍历每个 JSON 文件，收集 image 名称
    for json_file in json_files:
        json_path = os.path.join(json_folder, json_file)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for image in data.get("images", []):
                image_names.add(image["file_name"])

    # 确保目标文件夹存在
    if not os.path.exists(image_target_folder):
        os.makedirs(image_target_folder)

    # 遍历源文件夹中的所有文件，复制匹配的图像
    for image_name in image_names:
        source_image_path = os.path.join(image_source_folder, image_name)
        target_image_path = os.path.join(image_target_folder, image_name)
        if os.path.exists(source_image_path):
            shutil.copy2(source_image_path, target_image_path)
            print(f"已复制: {image_name}")

if __name__ == "__main__":

    json_folder = r"E:\SUBPJ\GIO\aiba\dataset\ap-10k\ap-10k\annotations\1"  # 替换为包含 JSON 文件的文件夹路径
    image_source_folder = r"E:\SUBPJ\GIO\aiba\dataset\ap-10k\ap-10k\data"  # 替换为源图像文件夹路径
    image_target_folder = r"E:\SUBPJ\GIO\aiba\dataset\ap-10k\ap-10k\img"  # 替换为目标图像文件夹路径

    copy_images_from_json_folder(json_folder, image_source_folder, image_target_folder)