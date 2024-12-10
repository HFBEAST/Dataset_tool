import os
import random
import cv2
import numpy as np
import albumentations as A

def simulate_night_vision():
    return A.Compose([
        A.ToGray(num_output_channels=3, method='desaturation', p=1)
    ])

# 所有的处理操作列表
operations = [
    simulate_night_vision(),
]

def process_images(folder_path):
    """
    处理指定文件夹中的图像，按照定义的增强操作。

    操作逻辑：
    - 对于每个增强操作：
        - 读取文件夹中的所有图像文件路径。
        - 随机选择50%的图像进行处理。
        - 对选中的图像应用增强操作。
        - 将处理后的图像覆盖保存到原文件夹中。

    参数影响：
    - 每次处理会覆盖原始图像，因此建议在运行前备份原始数据。

    参数：
    - folder_path: 图像文件夹的路径。
    """
    for operation in operations:
        # 获取文件夹中的所有图像路径
        image_paths = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(('jpg', 'png', 'jpeg', 'bmp', 'tif', 'tiff'))
        ]
        # 计算选择的图像数量（50%）
        num_images = len(image_paths)
        num_selected = max(num_images, num_images)  # 确保至少选择一张图像
        # 从中随机选择50%的图像
        selected_images = random.sample(image_paths, num_selected)
        for img_path in selected_images:
            # 读取图像
            image = cv2.imread(img_path)
            if image is None:
                print(f"警告：无法读取图像 {img_path}，已跳过。")
                continue
            # 转换颜色空间为 RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # 应用数据增强操作
            augmented = operation(image=image)
            image_aug = augmented['image']
            # 转回 BGR 颜色空间
            image_aug = cv2.cvtColor(image_aug, cv2.COLOR_RGB2BGR)
            # 保存图像，覆盖原文件
            cv2.imwrite(img_path, image_aug)
        print(f"已完成操作：{operation}")

if __name__ == "__main__":
    folder_path = r'H:\0_program\My_learn\YOLO\YoloV11\datasets\horse_pose\images\change'  # 请替换为您的实际文件夹路径
    process_images(folder_path)
