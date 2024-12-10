import pandas as pd
import json
import os
from PIL import Image


def convert_csv_to_labelme(csv_file, images_dir, output_dir):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 读取CSV文件，前三行为多级列头
    try:
        df = pd.read_csv(csv_file, header=[0, 1, 2])
    except Exception as e:
        print(f"无法读取CSV文件 {csv_file}，错误: {e}")
        return

    # 打印列头结构（用于调试）
    print("列头结构:")
    for col in df.columns:
        print(col)

    # 提取所有身体部位名称（跳过第一列）
    bodyparts = []
    columns = df.columns
    for col in columns:
        if col[0] != 'scorer' and col[2] in ['x', 'y']:
            if col[1] not in bodyparts:
                bodyparts.append(col[1])

    # 打印提取的身体部位（用于调试）
    print("\n提取的身体部位:")
    print(bodyparts)

    # 遍历每一行（每张图像）
    for index, row in df.iterrows():
        # 获取图像名称，位于第一列
        try:
            image_name = row[('scorer', 'bodyparts', 'coords')]
        except KeyError:
            print(f"行 {index} 缺少图像名称，跳过。")
            continue

        if pd.isna(image_name):
            print(f"行 {index} 图像名称为空，跳过。")
            continue

        image_path = os.path.join(images_dir, image_name)

        if not os.path.exists(image_path):
            print(f"图像文件 {image_path} 不存在，跳过。")
            continue

        # 打开图像并获取尺寸
        try:
            with Image.open(image_path) as img:
                width, height = img.size
        except Exception as e:
            print(f"无法打开图像 {image_path}，错误: {e}")
            continue

        # 提取所有有效的关键点
        points = []
        shapes = []
        for part in bodyparts:
            # 获取对应的(x, y)坐标
            try:
                x = row[('Byron', part, 'x')]
                y = row[('Byron', part, 'y')]
            except KeyError:
                print(f"图像 {image_name} 中缺少身体部位 {part} 的坐标，跳过该点。")
                continue

            if pd.notna(x) and pd.notna(y):
                try:
                    x = float(x)
                    y = float(y)
                except ValueError:
                    print(f"图像 {image_name} 中的 {part} 坐标无效，跳过该点。")
                    continue

                points.append([x, y])
                shape = {
                    "label": part,
                    "points": [[x, y]],
                    "group_id": None,
                    "shape_type": "point",
                    "flags": {}
                }
                shapes.append(shape)

        if not points:
            print(f"图像 {image_name} 没有有效的关键点，跳过。")
            continue

        # 计算检测框（最小矩形）
        xs, ys = zip(*points)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # 创建检测框形状
        rectangle_shape = {
            "label": "bounding_box",
            "points": [
                [min_x, min_y],
                [max_x, max_y]
            ],
            "group_id": None,
            "shape_type": "rectangle",
            "flags": {}
        }

        # 合并所有形状
        shapes = [rectangle_shape] + shapes

        # 创建JSON结构
        labelme_json = {
            "version": "5.5.0",
            "flags": {},
            "shapes": shapes,
            "imagePath": image_name,
            "imageData": None,  # 可以留空，LabelMe会从 imagePath 加载图像
            "imageHeight": height,
            "imageWidth": width
        }

        # 定义JSON文件的保存路径
        json_filename = os.path.splitext(image_name)[0] + '.json'
        json_path = os.path.join(output_dir, json_filename)

        # 写入JSON文件
        try:
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(labelme_json, json_file, ensure_ascii=False, indent=4)
            print(f"成功生成 {json_path}")
        except Exception as e:
            print(f"无法写入JSON文件 {json_path}，错误: {e}")

        # 验证生成的JSON是否有效
        try:
            with open(json_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            print(f"{json_filename} 是一个有效的JSON文件。")
        except json.JSONDecodeError as e:
            print(f"{json_filename} 是不合法的JSON文件，错误: {e}")


# 示例调用
if __name__ == "__main__":
    # 配置部分
    CSV_FILE = r'2333.csv'  # CSV文件路径
    IMAGES_DIR = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\Sample17'  # 图片所在文件夹路径
    OUTPUT_DIR = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\img_json'  # 输出JSON文件的文件夹路径

    convert_csv_to_labelme(CSV_FILE, IMAGES_DIR, OUTPUT_DIR)
