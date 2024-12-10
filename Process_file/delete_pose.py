import json
import os
import shutil


def filter_horse_label(input_json_path, output_folder):
    # 检查输入文件是否存在
    if not os.path.isfile(input_json_path):
        print(f"输入文件不存在: {input_json_path}")
        return

    # 读取原始 JSON 文件
    with open(input_json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return

    # 过滤出 label 为 "horse" 的 shapes
    filtered_shapes = [shape for shape in data.get('shapes', []) if shape.get('label') == 'horse']
    data['shapes'] = filtered_shapes

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取原文件名
    file_name = os.path.basename(input_json_path)

    # 构建输出文件路径
    output_json_path = os.path.join(output_folder, file_name)

    # 写入新的 JSON 文件
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 复制对应的图片文件到输出文件夹（如果需要）
    image_path = os.path.join(os.path.dirname(input_json_path), data.get('imagePath', ''))
    if os.path.isfile(image_path):
        shutil.copy(image_path, os.path.join(output_folder, data.get('imagePath')))
        print(f"已复制图片文件到: {output_folder}")
    else:
        print(f"未找到对应的图片文件: {image_path}")

    print(f"已保存过滤后的 JSON 文件到: {output_json_path}")


# 示例用法
if __name__ == "__main__":
    # 替换为您的 JSON 文件路径
    input_json = r'E:\PJ\GIO\aiba\dataset\archive_dataset(E8A)_checked\sum_E8A'

    # 替换为您想要保存的文件夹路径
    output_folder = r'E:\PJ\GIO\aiba\dataset\archive_dataset(E8A)_checked\det_json'

    for files in os.listdir(input_json):
        if files.endswith('.json'):
            filter_horse_label(os.path.join(input_json, files), output_folder)

