import json
import os
import glob

# 定义关键点的顺序
KEYPOINTS_ORDER = [
    "L_Eye",
    "R_Eye",
    "L_EarBase",
    "R_EarBase",
    "Nose",
    "Throat",
    "TailBase",
    "Withers",
    "L_F_Elbow",
    "R_F_Elbow",
    "L_B_Elbow",
    "R_B_Elbow",
    "L_F_Knee",
    "R_F_Knee",
    "L_B_Knee",
    "R_B_Knee",
    "L_F_Paw",
    "R_F_Paw",
    "L_B_Paw",
    "R_B_Paw"
]


def convert_labelme_to_yolo_multiple(json_file, output_txt_path):
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        image_width = data.get('imageWidth')
        image_height = data.get('imageHeight')
        image_path = data.get('imagePath')

        if not image_width or not image_height or not image_path:
            print(f"警告: 文件 '{json_file}' 中缺少必要的图像信息。")
            return

        image_name = os.path.splitext(os.path.basename(image_path))[0]

        shapes = data.get('shapes', [])

        # 初始化列表以存储所有对象的YOLO行
        yolo_lines = []

        i = 0
        while i < len(shapes):
            shape = shapes[i]
            if shape.get('label') == 'horse' and shape.get('shape_type') == 'rectangle':
                # 提取边界框
                coords = shape.get('points', [])
                if len(coords) != 2:
                    print(f"警告: 文件 '{json_file}' 中的 'horse' 边界框点数不正确。")
                    i += 1
                    continue

                x_min = min(coord[0] for coord in coords)
                y_min = min(coord[1] for coord in coords)
                x_max = max(coord[0] for coord in coords)
                y_max = max(coord[1] for coord in coords)
                bounding_box = (x_min, y_min, x_max, y_max)

                # 计算边界框的中心坐标和宽高，归一化
                box_center_x = (x_min + x_max) / 2 / image_width
                box_center_y = (y_min + y_max) / 2 / image_height
                box_width = (x_max - x_min) / image_width
                box_height = (y_max - y_min) / image_height

                # 初始化关键点字典
                keypoints_dict = {kp: (0, 0, 0) for kp in KEYPOINTS_ORDER}

                # 处理当前"horse"后的关键点，直到下一个"horse"或结束
                i += 1
                while i < len(shapes) and not (
                        shapes[i].get('label') == 'horse' and shapes[i].get('shape_type') == 'rectangle'):
                    kp_shape = shapes[i]
                    if kp_shape.get('shape_type') == 'point' and kp_shape.get('label') in keypoints_dict:
                        kp_points = kp_shape.get('points', [])
                        if len(kp_points) != 1:
                            print(f"警告: 文件 '{json_file}' 中的关键点 '{kp_shape.get('label')}' 点数不正确。")
                            i += 1
                            continue
                        x, y = kp_points[0]
                        keypoints_dict[kp_shape.get('label')] = (x / image_width, y / image_height, 2)  # 归一化并设为可见
                    else:
                        print(f"警告: 文件 '{json_file}' 中的未知关键点标签 '{kp_shape.get('label')}' 被忽略。")
                    i += 1

                # 构建YOLO行
                class_id = 0  # 类别ID为0，您可以根据需要修改
                yolo_line = f"{class_id} {box_center_x:.6f} {box_center_y:.6f} {box_width:.6f} {box_height:.6f}"

                # 添加关键点信息
                for kp in KEYPOINTS_ORDER:
                    x, y, visibility = keypoints_dict[kp]
                    if visibility == 2:
                        yolo_line += f" {x:.6f} {y:.6f} {visibility}"
                    else:
                        yolo_line += " 0 0 0"

                yolo_lines.append(yolo_line)
            else:
                i += 1  # 如果不是"horse"的边界框，继续下一个

        if not yolo_lines:
            print(f"警告: 文件 '{json_file}' 中未检测到任何 'horse' 对象。")

        # 写入TXT文件
        with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
            for line in yolo_lines:
                txt_file.write(line + '\n')

        print(f"转换成功: {output_txt_path}")

    except Exception as e:
        print(f"错误: 转换文件 '{json_file}' 时发生异常: {e}")


def convert_labelme_to_yolo_dataset(root_json_dir, root_output_dir):
    # 使用 os.walk 递归遍历所有子目录
    for dirpath, _, filenames in os.walk(root_json_dir):
        for filename in filenames:
            if filename.lower().endswith('.json'):
                json_file_path = os.path.join(dirpath, filename)

                # 构建相对于根目录的相对路径
                relative_path = os.path.relpath(dirpath, root_json_dir)

                # 构建输出TXT文件的目录
                output_dir = os.path.join(root_output_dir, relative_path)
                os.makedirs(output_dir, exist_ok=True)

                # 构建输出TXT文件的完整路径
                txt_filename = os.path.splitext(filename)[0] + '.txt'
                output_txt_path = os.path.join(output_dir, txt_filename)

                # 进行转换
                convert_labelme_to_yolo_multiple(json_file_path, output_txt_path)

    print("所有JSON文件已转换完成。")


# 批量转换示例用法
if __name__ == "__main__":
    # 设置包含JSON文件的根目录和输出根目录
    root_json_directory = r"E:\PJ\GIO\aiba\dataset\pose\0_horse\yolo\aiba"  # 替换为包含JSON文件的根目录
    root_output_directory = r"E:\PJ\GIO\aiba\dataset\pose\0_horse\yolo\aiba\labels"  # 替换为您希望保存TXT文件的根目录

    convert_labelme_to_yolo_dataset(root_json_directory, root_output_directory)
