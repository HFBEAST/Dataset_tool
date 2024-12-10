import json
import os

def change_labels_to_horse(input_json_path, output_json_path=None):
    """
    将JSON文件中所有'shape'的'label'字段更改为'horse'。

    :param input_json_path: 输入的JSON文件路径
    :param output_json_path: 输出的JSON文件路径。如果未指定，将覆盖原文件
    """
    # 检查输入文件是否存在
    if not os.path.isfile(input_json_path):
        print(f"输入文件不存在: {input_json_path}")
        return

    # 读取JSON数据
    try:
        with open(input_json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"读取JSON文件失败: {e}")
        return

    # 检查'shapes'键是否存在且为列表
    if 'shapes' not in data or not isinstance(data['shapes'], list):
        print("JSON结构不符合预期：缺少'shapes'键或'shapes'不是一个列表。")
        return

    # 修改每个shape的'label'为'horse'
    shape = data['shapes'][0]
    original_label = shape.get('label', None)
    shape['label'] = 'horse'
    print(f"将标签 '{original_label}' 改为 'horse'.")

    # 如果未指定输出路径，覆盖原文件
    if output_json_path is None:
        output_json_path = input_json_path

    # 写入修改后的JSON数据
    try:
        with open(output_json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"标签已成功更改并保存到: {output_json_path}")
    except Exception as e:
        print(f"保存修改后的JSON文件失败: {e}")

if __name__ == "__main__":

    input_path = r'E:\SUBPJ\GIO\aiba\dataset\horse10_190_labelme'  # 替换为你的JSON文件路径
    output_path =  r'E:\SUBPJ\GIO\aiba\dataset\233'

    filelist = os.listdir(input_path)

    for file in filelist:
        name, ext = os.path.splitext(file)
        if ext == '.json':
            input_json = os.path.join(input_path, file)
            output_json = os.path.join(output_path, file)
            # 示例用法

            change_labels_to_horse(input_json, output_json)
