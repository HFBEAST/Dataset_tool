import os
import shutil
import json
import argparse
import random
import numpy as np
from PIL import Image, ImageDraw
from sklearn.model_selection import train_test_split

# 假设 labelme2coco.utils 和 labelme2coco.image_utils 模块已存在
# 如果不存在，请确保这些模块的功能已被正确实现
from labelme2coco.utils import create_dir, list_jsons_recursively
from labelme2coco.image_utils import read_image_shape_as_dict


class Labelme2COCO:
    def __init__(self, labelme_folder='', save_json_path='./new.json'):
        """
        Args:
            labelme_folder: folder that contains labelme annotations and image files
            save_json_path: path for coco json to be saved
        """
        self.save_json_path = save_json_path
        self.images = []
        self.categories = []
        self.annotations = []
        self.label_set = set()
        self.annID = 1
        self.height = 0
        self.width = 0

        # Create save directory
        save_json_dir = os.path.dirname(save_json_path)
        create_dir(save_json_dir)

        # Get list of JSON files
        _, labelme_json = list_jsons_recursively(labelme_folder)
        self.labelme_json = labelme_json

    def data_transfer(self):
        for num, json_path in enumerate(self.labelme_json):
            print(json_path)
            with open(json_path, 'r', encoding='utf-8') as fp:
                # Load JSON
                data = json.load(fp)
                self.images.append(self.image(data, num, json_path))
                for shapes in data.get('shapes', []):
                    label = shapes['label']
                    self.label_set.add(label)
                    points = shapes['points']
                    self.annotations.append(self.annotation(points, label, num))
                    self.annID += 1

    def image(self, data, num, json_path):
        image = {}
        # Get image path
        _, img_extension = os.path.splitext(data["imagePath"])
        image_path = os.path.join(os.path.dirname(json_path), data["imagePath"])
        img_shape = read_image_shape_as_dict(image_path)
        height, width = img_shape['height'], img_shape['width']

        image['height'] = height
        image['width'] = width
        image['id'] = int(num + 1)
        image['file_name'] = os.path.basename(image_path)

        self.height = height
        self.width = width

        return image

    def category(self, label):
        category = {}
        category['supercategory'] = label
        category['id'] = int(len(self.label_set))  # ID 从1开始
        category['name'] = label

        return category

    def annotation(self, points, label, num):
        annotation = {}
        annotation['iscrowd'] = 0
        annotation['image_id'] = int(num + 1)

        annotation['bbox'] = list(map(float, self.getbbox(points)))

        # Coarsely from bbox to segmentation
        x = annotation['bbox'][0]
        y = annotation['bbox'][1]
        w = annotation['bbox'][2]
        h = annotation['bbox'][3]
        annotation['segmentation'] = [np.asarray(points).flatten().tolist()]

        annotation['category_id'] = self.getcatid(label)
        annotation['id'] = int(self.annID)
        # Add area info
        annotation['area'] = float(w * h)  # 使用边界框面积

        return annotation

    def getcatid(self, label):
        for categorie in self.categories:
            if label == categorie['name']:
                return categorie['id']
        return 1

    def getbbox(self, points):
        polygons = points
        mask = self.polygons_to_mask([self.height, self.width], polygons)
        return self.mask2box(mask)

    def mask2box(self, mask):
        index = np.argwhere(mask == 1)
        rows = index[:, 0]
        cols = index[:, 1]

        left_top_r = np.min(rows)  # y
        left_top_c = np.min(cols)  # x

        right_bottom_r = np.max(rows)
        right_bottom_c = np.max(cols)

        return [left_top_c, left_top_r, right_bottom_c - left_top_c, right_bottom_r - left_top_r]  # [x1,y1,w,h]

    def polygons_to_mask(self, img_shape, polygons):
        mask = np.zeros(img_shape, dtype=np.uint8)
        mask = Image.fromarray(mask)
        xy = list(map(tuple, polygons))
        ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
        mask = np.array(mask, dtype=bool)
        return mask

    def data2coco(self):
        data_coco = {}
        data_coco['images'] = self.images
        data_coco['categories'] = self.categories
        data_coco['annotations'] = self.annotations
        return data_coco

    def save_json(self):
        self.data_transfer()

        # Create categories
        sorted_labels = sorted(self.label_set)
        self.categories = []
        for idx, label in enumerate(sorted_labels, start=1):
            self.categories.append(self.category(label))

        self.data_coco = self.data2coco()

        with open(self.save_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data_coco, f, indent=4, separators=(',', ': '), cls=MyEncoder)


# Type check when saving JSON files
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


def split_dataset(input_dir, output_dir, split_ratios):
    """
    将数据集按比例划分为 train, val, test，并将图像与对应的 JSON 文件放在同一文件夹中。

    参数:
    input_dir (str): 包含图像和JSON文件的文件夹路径.
    output_dir (str): 输出的文件夹路径.
    split_ratios (tuple): (train_ratio, val_ratio, test_ratio) 三个数据集的比例.
    """
    # 获取所有图像文件和对应的 JSON 文件
    image_extensions = ('.jpg', '.jpeg', '.png')
    all_files = os.listdir(input_dir)
    image_files = [f for f in all_files if f.lower().endswith(image_extensions)]

    # 确保每个图像都有对应的 JSON 文件
    paired_files = []
    for img in image_files:
        base_name = os.path.splitext(img)[0]
        json_file = base_name + '.json'
        if json_file in all_files:
            paired_files.append((img, json_file))
        else:
            print(f"警告: 图像 '{img}' 没有对应的 JSON 文件，已跳过。")

    if not paired_files:
        raise ValueError("没有找到任何匹配的图像和 JSON 文件。")

    # 打乱数据
    random.seed(42)
    random.shuffle(paired_files)

    total = len(paired_files)
    train_ratio, val_ratio, test_ratio = split_ratios
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    train_files = paired_files[:train_end]
    val_files = paired_files[train_end:val_end]
    test_files = paired_files[val_end:]

    # 创建输出文件夹
    for split, files in zip(['train', 'val', 'test'], [train_files, val_files, test_files]):
        split_dir = os.path.join(output_dir, split)
        if not os.path.exists(split_dir):
            os.makedirs(split_dir)
        for img, json_f in files:
            shutil.copy(os.path.join(input_dir, img), os.path.join(split_dir, img))
            shutil.copy(os.path.join(input_dir, json_f), os.path.join(split_dir, json_f))
        print(f"{split.capitalize()} 集合: 复制了 {len(files)} 对文件。")


def generate_labels_txt(annotations_dir, labels_txt_path):
    """
    遍历 annotations 目录下的所有 JSON 文件，收集所有标签，并生成 labels.txt 文件。

    参数:
    annotations_dir (str): 保存 COCO JSON 文件的目录.
    labels_txt_path (str): labels.txt 文件的保存路径.
    """
    label_set = set()

    # 遍历所有 COCO JSON 文件
    for json_file in os.listdir(annotations_dir):
        if json_file.endswith('.json'):
            json_path = os.path.join(annotations_dir, json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for category in data.get('categories', []):
                    label_set.add(category['name'])

    # 添加 __background__ 和 __ignore__ 标签
    sorted_labels = sorted(label_set)
    sorted_labels = ['__ignore__', '__background__'] + sorted_labels

    # 写入 labels.txt
    with open(labels_txt_path, 'w', encoding='utf-8') as f:
        for label in sorted_labels:
            f.write(f"{label}\n")

    print(f"labels.txt 已生成，包含 {len(sorted_labels)} 个标签。")


def main(total_data_dir):
    parser = argparse.ArgumentParser(description='将数据集按比例划分并转换为 COCO 格式.')
    parser.add_argument('--total_target_dir', type=str, default=total_data_dir, help='总目标文件夹路径，包含 train, val, test 子文件夹')
    parser.add_argument('--ratios', type=float, nargs=3, default=[0.7, 0.2, 0.1],
                        help='train, val, test 数据集的比例 (默认为 0.7, 0.2, 0.1)')
    parser.add_argument('--input_dir', type=str, default='', help='原始输入文件夹路径，包含所有图像和 JSON 文件')
    args = parser.parse_args()

    total_target_dir = args.total_target_dir
    ratios = args.ratios
    input_dir = args.input_dir

    if input_dir:
        # 如果指定了 input_dir，则先进行数据划分
        print("开始数据划分...")
        split_dataset(input_dir, total_target_dir, ratios)
        print("数据划分完成。")

    # 创建 annotations 文件夹
    annotations_dir = os.path.join(total_target_dir, 'annotations')
    create_dir(annotations_dir)

    # 处理每个 split 文件夹
    splits = ['train', 'val', 'test']
    for split in splits:
        split_folder = os.path.join(total_target_dir, split)
        if not os.path.exists(split_folder):
            print(f"警告: {split} 文件夹不存在，已跳过。")
            continue

        # 定义保存的 COCO JSON 文件路径
        save_json_path = os.path.join(annotations_dir, f"instances_{split}.json")

        print(f"正在转换 {split} 集合...")
        converter = Labelme2COCO(labelme_folder=split_folder, save_json_path=save_json_path)
        converter.save_json()
        print(f"{split} 集合转换完成，COCO JSON 保存至 {save_json_path}")

    # 生成 labels.txt
    labels_txt_path = os.path.join(annotations_dir, 'labels.txt')
    generate_labels_txt(annotations_dir, labels_txt_path)
    print("所有转换和标签文件生成完成。")


if __name__ == "__main__":
    total_data_dir = r"E:\PJ\GIO\aiba\dataset\horse_6500_aiba_20241122"
    main(total_data_dir)
