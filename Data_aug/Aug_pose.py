import os
import random
import cv2
import numpy as np
import albumentations as A
import json
import base64


# 定义数据增强操作
def add_noise():
    """
    添加高斯噪声到图像。
    """
    return A.Compose([
        A.GaussNoise(var_limit=(20.0, 40.0), mean=100, p=1)
    ])


def change_exposure():
    """
    随机改变图像的曝光度，模拟不同的曝光效果。
    """
    return A.Compose([
        A.RandomGamma(gamma_limit=(90, 110), p=1)
    ])


def simulate_night_vision():
    """
    模拟夜视效果，将图像转换为灰度。
    """
    return A.Compose([
        A.ToGray(num_output_channels=3, method='desaturation', p=1)
    ])


def change_color():
    """
    通过RGB通道偏移模拟颜色变化。
    """
    return A.Compose([
        A.RGBShift(r_shift_limit=(-20, 20), g_shift_limit=(-20, 20), b_shift_limit=(-20, 20), p=1)
    ])


def change_InvertImg():
    """
    反转图像颜色。
    """
    return A.Compose([
        A.InvertImg(p=1)
    ])


def add_rain_effect():
    """
    添加下雨效果到图像。
    """
    return A.Compose([
        A.RandomRain(
            slant_lower=-10,
            slant_upper=10,
            drop_length=15,
            drop_width=1,
            drop_color=(200, 200, 200),
            blur_value=3,
            brightness_coefficient=0.8,
            rain_type='torrential',
            p=1
        )
    ])


def blur_image():
    """
    对图像应用模糊效果。
    """
    return A.Compose([
        A.Blur(blur_limit=5, p=1)
    ])


def mosaic_image():
    """
    模拟马赛克效果，对图像进行下采样再上采样。
    """
    return A.Compose([
        A.Downscale(scale_min=0.2, scale_max=0.30, interpolation=cv2.INTER_NEAREST, p=1)
    ])


def simulate_sunset():
    """
    模拟夕阳等光线变化，添加太阳耀斑效果。
    """
    return A.Compose([
        A.RandomSunFlare(
            flare_roi=(0, 0, 1, 1),
            angle_range=(0, 1),
            src_radius=100,
            num_flare_circles_range=(3, 6),
            method='overlay',
            p=1
        )
    ])


def to_VerticalFlip():
    """
    垂直翻转图像。
    """
    return A.Compose([
        A.VerticalFlip(p=1)
    ])


def to_HorizontalFlip():
    """
    水平翻转图像。
    """
    return A.Compose([
        A.HorizontalFlip(p=1)
    ])


# 所有的处理操作列表，包含操作名称
operations = [
    ("添加高斯噪声", add_noise()),
    ("改变曝光度", change_exposure()),
    # ("模拟夜视效果", simulate_night_vision()),
    ("添加下雨效果", add_rain_effect()),
    # ("应用模糊效果", blur_image()),
    # ("应用马赛克效果", mosaic_image()),
    ("模拟夕阳效果", simulate_sunset()),
    ("改变颜色", change_color()),
    ("反转图像颜色", change_InvertImg()),
    ("垂直翻转", to_VerticalFlip()),
    ("水平翻转", to_HorizontalFlip())
]


def read_json(json_path):
    """
    读取JSON标注文件。
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def write_json(json_path, data):
    """
    写入JSON标注文件。
    """
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def flip_bounding_box(points, image_width, image_height, flip_type):
    """
    根据翻转类型调整检测框坐标。

    参数：
    - points: 检测框的两个点 [[x1, y1], [x2, y2]]
    - image_width: 图像宽度
    - image_height: 图像高度
    - flip_type: 'vertical' 或 'horizontal'

    返回：
    - 修改后的检测框坐标 [[new_x1, new_y1], [new_x2, new_y2]]
    """
    (x1, y1), (x2, y2) = points
    if flip_type == 'vertical':
        new_y1 = image_height - y1
        new_y2 = image_height - y2
        return [[x1, new_y1], [x2, new_y2]]
    elif flip_type == 'horizontal':
        new_x1 = image_width - x1
        new_x2 = image_width - x2
        return [[new_x1, y1], [new_x2, y2]]
    else:
        return points  # 无需翻转


def flip_point(point, image_width, image_height, flip_type):
    """
    根据翻转类型调整单个点的坐标。

    参数：
    - point: 单个点的坐标 [x, y]
    - image_width: 图像宽度
    - image_height: 图像高度
    - flip_type: 'vertical' 或 'horizontal'

    返回：
    - 修改后的点坐标 [new_x, new_y]
    """
    x, y = point
    if flip_type == 'vertical':
        new_y = image_height - y
        return [x, new_y]
    elif flip_type == 'horizontal':
        new_x = image_width - x
        return [new_x, y]
    else:
        return point  # 无需翻转


def update_annotation(json_path, image_shape, flip_type):
    """
    更新标注文件中的检测框或点坐标。

    参数：
    - json_path: JSON标注文件路径
    - image_shape: (高度, 宽度, 通道数)
    - flip_type: 'vertical' 或 'horizontal'
    """
    if not os.path.exists(json_path):
        print(f"警告：标注文件 {json_path} 不存在，已跳过。")
        return

    data = read_json(json_path)
    image_height, image_width = data.get('imageHeight'), data.get('imageWidth')
    if image_height is None or image_width is None:
        # 如果JSON文件中没有imageHeight或imageWidth，则从图像形状中获取
        image_height, image_width = image_shape[:2]

    for shape in data.get('shapes', []):
        shape_type = shape.get('shape_type', '').lower()
        points = shape.get('points', [])

        if not points:
            continue  # 如果没有点，跳过

        if shape_type == 'rectangle' and len(points) == 2:
            # 处理矩形
            flipped_points = flip_bounding_box(points, image_width, image_height, flip_type)
            # 确保左上角和右下角
            x_coords = [pt[0] for pt in flipped_points]
            y_coords = [pt[1] for pt in flipped_points]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            shape['points'] = [[x_min, y_min], [x_max, y_max]]

        elif shape_type == 'point' and len(points) == 1:
            # 处理单个点
            original_point = points[0]
            flipped_point = flip_point(original_point, image_width, image_height, flip_type)
            shape['points'] = [flipped_point]

        else:
            # 其他形状类型或不符合预期的点数量，暂不处理
            print(f"警告：未处理的形状类型或点数量：{shape_type}, 点数：{len(points)}")
            continue

    write_json(json_path, data)


def update_imageData(json_path, image_aug_bgr):
    """
    更新标注文件中的 imageData 字段为最新的图像数据的 base64 编码。

    参数：
    - json_path: JSON标注文件路径
    - image_aug_bgr: 增强后的图像数据，BGR格式
    """
    if not os.path.exists(json_path):
        print(f"警告：标注文件 {json_path} 不存在，已跳过 imageData 更新。")
        return

    try:
        # Encode the augmented image to base64
        _, buffer = cv2.imencode('.jpg', image_aug_bgr)
        image_bytes = buffer.tobytes()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # Read JSON
        data = read_json(json_path)
        data['imageData'] = image_base64

        # Write JSON
        write_json(json_path, data)
    except Exception as e:
        print(f"错误更新 imageData in {json_path}：{e}")


def update_all_imageData(folder_path):
    """
    遍历文件夹中的所有图像和对应的JSON文件，更新 imageData 字段为最新的图像数据的 base64 编码。

    参数：
    - folder_path: 图像文件夹的路径。
    """
    image_paths = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(('jpg', 'png', 'jpeg', 'bmp', 'tif', 'tiff'))
    ]

    for img_path in image_paths:
        try:
            # 获取图像基名（不带扩展名）
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            json_path = os.path.join(folder_path, base_name + '.json')

            # 读取增强后的图像
            image_aug_bgr = cv2.imread(img_path)
            if image_aug_bgr is None:
                print(f"警告：无法读取图像 {img_path}，已跳过 imageData 更新。")
                continue

            # 更新 imageData 字段
            update_imageData(json_path, image_aug_bgr)

        except Exception as e:
            print(f"错误更新 imageData for 图像 {img_path}：{e}")
            continue


def process_images(folder_path):
    """
    处理指定文件夹中的图像，按照定义的增强操作。

    操作逻辑：
    - 对于每个增强操作：
        - 读取文件夹中的所有图像文件路径。
        - 随机选择50%的图像进行处理。
        - 对选中的图像应用增强操作。
        - 如果操作是垂直或水平翻转，则同步更新标注文件中的检测框或点坐标。
        - 将处理后的图像覆盖保存到原文件夹中。

    参数影响：
    - 每次处理会覆盖原始图像和标注文件，因此建议在运行前备份原始数据。

    参数：
    - folder_path: 图像文件夹的路径。
    """
    for operation_name, operation in operations:
        # 获取文件夹中的所有图像路径
        image_paths = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(('jpg', 'png', 'jpeg', 'bmp', 'tif', 'tiff'))
        ]
        if not image_paths:
            print(f"文件夹 {folder_path} 中没有找到图像文件。")
            continue

        # 计算选择的图像数量（约50%）
        num_images = len(image_paths)
        num_selected = max(1, num_images // 2)  # 确保至少选择一张图像

        # 从中随机选择50%的图像
        selected_images = random.sample(image_paths, num_selected)

        for img_path in selected_images:
            try:
                # 读取图像
                image = cv2.imread(img_path)
                if image is None:
                    print(f"警告：无法读取图像 {img_path}，已跳过。")
                    continue

                # 获取图像基名（不带扩展名）
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                json_path = os.path.join(folder_path, base_name + '.json')

                # 读取标注文件获取图像尺寸
                if os.path.exists(json_path):
                    data = read_json(json_path)
                    image_height = data.get('imageHeight')
                    image_width = data.get('imageWidth')
                    if image_height is None or image_width is None:
                        # 如果JSON文件中没有imageHeight或imageWidth，则从图像形状中获取
                        image_height, image_width = image.shape[:2]
                else:
                    print(f"警告：标注文件 {json_path} 不存在，已跳过图像 {img_path} 的标注更新。")
                    image_height, image_width = image.shape[:2]

                # 转换颜色空间为 RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # 应用数据增强操作
                augmented = operation(image=image_rgb)
                image_aug = augmented['image']

                # 转回 BGR 颜色空间
                image_aug_bgr = cv2.cvtColor(image_aug, cv2.COLOR_RGB2BGR)

                # 保存图像，覆盖原文件
                cv2.imwrite(img_path, image_aug_bgr)

                # 如果操作是垂直或水平翻转，则更新标注文件中的检测框或点坐标
                if operation_name in ["垂直翻转", "水平翻转"]:
                    flip_type = 'vertical' if operation_name == "垂直翻转" else 'horizontal'
                    update_annotation(json_path, image_aug.shape, flip_type)

            except Exception as e:
                print(f"错误处理图像 {img_path}：{e}")
                continue

        print(f"已完成操作：{operation_name}")

    # 所有增强操作完成后，统一更新所有图像的 imageData 字段
    print("开始更新所有图像的 imageData 字段为最新的 Base64 编码。")
    update_all_imageData(folder_path)
    print("已完成所有图像的 imageData 更新。")


if __name__ == "__main__":
    folder_path = r'E:\PJ\GIO\aiba\dataset\pose\0_sum_labelme_aug'  # 请替换为您的实际文件夹路径
    process_images(folder_path)
