import json
import os
import sys


def load_json(json_path):
    """
    加载 JSON 文件
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"加载 JSON 文件时出错: {json_path}\n错误信息: {e}")
        return None


def save_json(data, output_path):
    """
    保存 JSON 文件
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"已保存修改后的 JSON 文件: {output_path}")
    except Exception as e:
        print(f"保存 JSON 文件时出错: {output_path}\n错误信息: {e}")


def point_in_rectangle(point, rect):
    """
    检查点是否在矩形内
    :param point: (x, y)
    :param rect: ((x1, y1), (x2, y2))
    :return: True 如果点在矩形内，否则 False
    """
    x, y = point
    (x1, y1), (x2, y2) = rect
    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)
    return left <= x <= right and top <= y <= bottom


def filter_shapes(data, input_points):
    """
    过滤掉包含任意输入点的标注框
    :param data: JSON 数据
    :param input_points: List of (x, y) tuples
    :return: 修改后的 JSON 数据
    """
    original_count = len(data.get('shapes', []))
    filtered_shapes = []
    removed_shapes = []

    for shape in data.get('shapes', []):
        rect = shape.get('points', [])
        if len(rect) != 2:
            # 如果不是矩形，保留该标注
            filtered_shapes.append(shape)
            continue
        rect_coords = ((rect[0][0], rect[0][1]), (rect[1][0], rect[1][1]))
        # 检查是否有任何点在矩形内
        contains = any(point_in_rectangle(pt, rect_coords) for pt in input_points)
        if not contains:
            filtered_shapes.append(shape)
        else:
            removed_shapes.append(shape)
            print(f"移除标注: 标签='{shape.get('label')}' 坐标={rect_coords}，因为包含指定点。")

    data['shapes'] = filtered_shapes
    removed_count = original_count - len(filtered_shapes)
    print(f"已移除 {removed_count} 个标注（总共 {original_count} 个标注）。\n")
    return data


def process_json_files(input_dir, output_dir, input_points):
    """
    处理指定目录下的所有 JSON 文件
    :param input_dir: 输入目录路径
    :param output_dir: 输出目录路径
    :param input_points: List of (x, y) tuples
    """
    if not os.path.isdir(input_dir):
        print(f"输入目录不存在: {input_dir}")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建输出目录: {output_dir}")

    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

    if not json_files:
        print(f"在目录中未找到 JSON 文件: {input_dir}")
        return

    print(f"找到 {len(json_files)} 个 JSON 文件，开始处理...\n")

    for filename in json_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        print(f"处理文件: {input_path}")

        data = load_json(input_path)
        if data is None:
            continue

        modified_data = filter_shapes(data, input_points)
        save_json(modified_data, output_path)

    print("所有文件处理完成。")


def main():
    # 定义输入和输出目录路径
    input_dir = r'D:\23333\archive_dataset\change_back_image_daytime_fullbody'  # 替换为您的输入目录路径
    output_dir = r'D:\23333\archive_dataset\1'  # 替换为您的输出目录路径

    # 定义需要检查的输入点列表，这里直接在脚本中定义
    input_points = [
        (632.0, 280.0),  # 示例点1
        (632.0, 420.0),
        (115.0, 440.0),
        (130.0, 460.0),
        (3.0, 396.0),
        (13.0, 476.0),
        (595.0, 343.0)# 示例点2
        # 可以根据需要添加更多点
    ]

    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"输入点: {input_points}\n")

    process_json_files(input_dir, output_dir, input_points)


if __name__ == "__main__":
    main()
