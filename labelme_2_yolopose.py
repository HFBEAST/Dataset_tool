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


def convert_labelme_to_yolo_multiple(json_dir, output_dir):
    # 获取所有JSON文件
    json_files = glob.glob(os.path.join(json_dir, "*.json"))

    if not json_files:
        print("警告: 在指定目录中未找到任何JSON文件。")
        return

    for json_file in json_files:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        image_width = data['imageWidth']
        image_height = data['imageHeight']
        image_name = os.path.splitext(os.path.basename(data['imagePath']))[0]

        shapes = data['shapes']

        # 初始化列表以存储所有对象的YOLO行
        yolo_lines = []

        i = 0
        while i < len(shapes):
            shape = shapes[i]
            if shape['label'] == 'horse' and shape['shape_type'] == 'rectangle':
                # 提取边界框
                coords = shape['points']
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
                        shapes[i]['label'] == 'horse' and shapes[i]['shape_type'] == 'rectangle'):
                    kp_shape = shapes[i]
                    if kp_shape['shape_type'] == 'point' and kp_shape['label'] in keypoints_dict:
                        x, y = kp_shape['points'][0]
                        keypoints_dict[kp_shape['label']] = (x / image_width, y / image_height, 2)  # 归一化并设为可见
                    else:
                        print(f"警告: 未知的关键点标签 '{kp_shape['label']}' 被忽略。")
                    i += 1

                # 构建YOLO行
                class_id = 0  # 类别ID为0
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

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 写入TXT文件
        txt_filename = os.path.join(output_dir, f"{image_name}.txt")
        with open(txt_filename, 'w', encoding='utf-8') as txt_file:
            for line in yolo_lines:
                txt_file.write(line + '\n')

        print(f"转换成功: {txt_filename}")


# 批量转换示例用法
if __name__ == "__main__":
    # 设置包含JSON文件的目录和输出目录
    json_directory = r"H:\0_program\My_learn\YOLO\YoloV11\datasets\horse_pose\labels\val"  # 替换为包含JSON文件的目录
    output_directory = r"H:\0_program\My_learn\YOLO\YoloV11\datasets\horse_pose\labels\val"  # 替换为您希望保存TXT文件的目录

    convert_labelme_to_yolo_multiple(json_directory, output_directory)
