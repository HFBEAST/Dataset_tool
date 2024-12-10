import os
import sys
import argparse

def get_file_stem(filename):
    """返回文件的主干名称（不含扩展名）。"""
    return os.path.splitext(filename)[0]

def is_image_file(filename, image_extensions):
    """判断文件是否为图片格式。"""
    return os.path.splitext(filename)[1].lower() in image_extensions

def find_corresponding_files(directory, image_extensions):
    """
    在指定目录中查找图片文件和 JSON 文件，建立它们的对应关系。

    返回两个集合：
    - images: 所有图片文件的主干名称
    - jsons: 所有 JSON 文件的主干名称
    """
    images = set()
    jsons = set()

    for entry in os.scandir(directory):
        if entry.is_file():
            filename = entry.name
            stem = get_file_stem(filename)
            if is_image_file(filename, image_extensions):
                images.add(stem)
            elif filename.lower().endswith('.json'):
                jsons.add(stem)

    return images, jsons

def delete_files(directory, stems, extension):
    """删除指定主干名称和扩展名的文件。"""
    for stem in stems:
        file_path = os.path.join(directory, f"{stem}{extension}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已删除: {file_path}")
            except Exception as e:
                print(f"删除失败: {file_path}. 错误: {e}")

def main(directory):
    # 定义支持的图片扩展名
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

    # 获取图片和 JSON 文件的主干名称
    images, jsons = find_corresponding_files(directory, image_extensions)

    # 找出没有对应 JSON 文件的图片
    images_without_json = images - jsons

    # 找出没有对应图片的 JSON 文件
    jsons_without_images = jsons - images

    if not images_without_json and not jsons_without_images:
        print("所有图片和 JSON 文件均一一对应，无需删除。")
        return

    # 删除没有对应 JSON 文件的图片
    for stem in images_without_json:
        for ext in image_extensions:
            file_path = os.path.join(directory, f"{stem}{ext}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"已删除无对应 JSON 文件的图片: {file_path}")
                except Exception as e:
                    print(f"删除失败: {file_path}. 错误: {e}")

    # 删除没有对应图片的 JSON 文件
    for stem in jsons_without_images:
        json_path = os.path.join(directory, f"{stem}.json")
        if os.path.exists(json_path):
            try:
                os.remove(json_path)
                print(f"已删除无对应图片的 JSON 文件: {json_path}")
            except Exception as e:
                print(f"删除失败: {json_path}. 错误: {e}")

    print("清理完成。")

if __name__ == "__main__":

    target_directory = r"E:\PJ\GIO\aiba\dataset\pose\0_sum_labelme_aug"

    if not os.path.isdir(target_directory):
        print(f"错误: '{target_directory}' 不是一个有效的文件夹路径。")
        sys.exit(1)

    main(target_directory)
