import json

def filter_json_by_category(input_file, output_file, target_category_id):
    # 读取原始 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 初始化新 JSON 数据结构
    new_data = {
        "images": [],
        "annotations": [],
        "categories": data["categories"]
    }

    # 用于存储符合条件的 image_id
    image_ids = set()

    # 遍历 annotations，找到 category_id 为目标值的项
    for annotation in data["annotations"]:
        if annotation["category_id"] == target_category_id:
            new_data["annotations"].append(annotation)
            image_ids.add(annotation["image_id"])

    # 遍历 images，找到 image_id 符合条件的项
    for image in data["images"]:
        if image["id"] in image_ids:
            new_data["images"].append(image)

    # 写入新的 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_file = r"E:\SUBPJ\GIO\aiba\dataset\ap-10k\ap-10k\annotations\ap10k-val-split1.json"  # 替换为你的输入 JSON 文件路径
    output_file = r"9.json"  # 替换为你的输出 JSON 文件路径
    target_category_id = 21  # 目标 category_id

    filter_json_by_category(input_file, output_file, target_category_id)