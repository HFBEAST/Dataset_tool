#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-----------------------------------------------------#
   @File : labelme2yolo.py
   @Time : 2024/4/27
   @Author : ChatGPT
   @Description :
   将YOLO数据集格式的文件夹中的所有 LabelMe 格式 JSON 文件转换为 YOLO 格式 TXT 文件
   - 不使用命令行参数，直接在脚本中设置参数
   - TXT 文件保存到 JSON 文件所在的文件夹中
   - 使用 JSON 文件中提供的图像尺寸信息
#-----------------------------------------------------#
"""

import json
import numpy as np
from pathlib import Path
import glob
import os

class LabelmeToYOLO:
    def __init__(
            self,
            root_dir: str,
            labels_file: str
            ):
        """
        初始化转换器

        :param root_dir: YOLO数据集格式的根目录路径
        :param labels_file: 包含所有类别名称的文件，每行一个类别
        """
        self.root_dir = Path(root_dir)
        self.labels_file = Path(labels_file)
        self.labels = []
        self.labels_out = []

        # 读取标签
        self.read_labels()

    def read_labels(self):
        """
        读取标签文件，忽略以 '_' 开头的标签
        """
        if not self.labels_file.exists():
            raise FileNotFoundError(f"标签文件未找到: {self.labels_file}")

        with self.labels_file.open('r', encoding='utf-8') as f:
            for line in f:
                label = line.strip()
                if label and not label.startswith('_'):
                    self.labels.append(label)
                    self.labels_out.append(label + '\n')
        self.classes = len(self.labels)
        if self.classes == 0:
            raise ValueError("没有有效的标签被读取。请检查标签文件。")

    def convert_all(self):
        """
        执行转换操作，将所有 JSON 文件转换为 YOLO TXT 文件
        """
        # 递归查找所有 JSON 文件
        json_files = list(self.root_dir.rglob('*.json'))
        if not json_files:
            print(f"在 {self.root_dir} 中未找到任何 JSON 文件。")
            return

        for json_file in json_files:
            try:
                self.json_to_txt(json_file)
                print(f"已转换: {json_file}")
            except Exception as e:
                print(f"转换失败: {json_file}，错误: {e}")

    def json_to_txt(self, json_file: Path):
        """
        将单个 JSON 文件转换为 YOLO 格式的 TXT 文件

        :param json_file: JSON 文件路径
        """
        with json_file.open('r', encoding='utf-8') as f:
            data = json.load(f)

        # 获取图像尺寸
        image_width = data.get('imageWidth', None)
        image_height = data.get('imageHeight', None)
        if image_width is None or image_height is None:
            raise ValueError(f"JSON 文件中缺少图像尺寸信息: {json_file}")

        txt_filename = json_file.stem + '.txt'
        txt_path = json_file.parent / txt_filename

        with txt_path.open('w', encoding='utf-8') as txt_file:
            for shape in data.get('shapes', []):
                label = shape.get('label', '').strip()
                shape_type = shape.get('shape_type', '').strip()

                if shape_type != "rectangle":
                    print(f"警告: 文件 {json_file} 包含非矩形标注 '{shape_type}'，已跳过。")
                    continue

                if label not in self.labels:
                    print(f"警告: 标签 '{label}' 不在标签列表中，已忽略。")
                    continue

                idx = self.labels.index(label)
                points = shape.get('points', [])

                if len(points) != 2:
                    print(f"警告: 文件 {json_file} 中的标注 '{label}' 点数不为2，已跳过。")
                    continue

                x_center, y_center, w, h = self.points_to_yolo_bbox(points, image_width, image_height)

                # 写入 YOLO 格式: <object-class> <x_center> <y_center> <width> <height>
                idx = 0
                annotation = f"{idx} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n"
                txt_file.write(annotation)

    def points_to_yolo_bbox(self, points: list, image_width: int, image_height: int) -> tuple:
        """
        将矩形的两个点转换为 YOLO 格式的边界框

        :param points: 包含两个点的列表，每个点是 [x, y]
        :param image_width: 图像宽度
        :param image_height: 图像高度
        :return: (x_center, y_center, width, height) 归一化后的坐标
        """
        if len(points) != 2:
            raise ValueError("points 参数必须包含两个点。")

        (x1, y1), (x2, y2) = points
        min_x = min(x1, x2)
        min_y = min(y1, y2)
        max_x = max(x1, x2)
        max_y = max(y1, y2)

        w = max_x - min_x
        h = max_y - min_y
        c_x = min_x + w / 2.0
        c_y = min_y + h / 2.0

        # 归一化
        c_x_norm = c_x / image_width
        c_y_norm = c_y / image_height
        w_norm = w / image_width
        h_norm = h / image_height

        return (c_x_norm, c_y_norm, w_norm, h_norm)

if __name__ == '__main__':
    # 设置参数
    root_dir = r'E:\PJ\GIO\aiba\dataset\pose\test\txt'  # YOLO数据集根目录路径
    labels_file = r'E:\PJ\GIO\aiba\dataset\pose\test\txt\labels.txt'  # 标签文件路径

    # 创建转换器实例
    converter = LabelmeToYOLO(
        root_dir=root_dir,
        labels_file=labels_file
    )

    # 执行转换
    converter.convert_all()
