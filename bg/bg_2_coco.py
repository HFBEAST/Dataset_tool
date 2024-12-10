import os
import json
from PIL import Image

def create_coco_json(image_dir, output_json, info=None, licenses=None):
    images = []
    annotations = []
    categories = []  # 可以根据需要添加类别

    # 遍历图片文件夹
    image_id = 1
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            filepath = os.path.join(image_dir, filename)
            try:
                with Image.open(filepath) as img:
                    width, height = img.size
                image_info = {
                    "id": image_id,
                    "file_name": filename,
                    "width": width,
                    "height": height
                }
                images.append(image_info)
                image_id += 1
            except Exception as e:
                print(f"无法打开图片 {filepath}: {e}")
                continue

    coco = {
        "info": info if info else {
            "description": "COCO dataset with background images only",
            "version": "1.0",
            "year": 2024
        },
        "licenses": licenses if licenses else [],
        "images": images,
        "annotations": annotations,
        "categories": categories  # 如果没有类别，可以留空
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(coco, f, ensure_ascii=False, indent=4)
    print(f"COCO JSON 文件已生成: {output_json}")

forlder_path = r'E:\PJ\GIO\aiba\dataset\no_horse\horse_bg'
# 使用示例
train_image_directory = forlder_path + r'\train'  # 替换为您的训练图片文件夹路径
val_image_directory = forlder_path + r'\val'      # 替换为您的验证图片文件夹路径
test_image_directory = forlder_path + r'\test'    # 替换为您的测试图片文件夹路径

train_output_json = 'instances_train.json'
val_output_json = 'instances_val.json'
test_output_json = 'instances_test.json'

# 生成训练集的 COCO JSON 文件
create_coco_json(train_image_directory, train_output_json)

# 生成验证集的 COCO JSON 文件
create_coco_json(val_image_directory, val_output_json)

# 生成测试集的 COCO JSON 文件
create_coco_json(test_image_directory, test_output_json)
