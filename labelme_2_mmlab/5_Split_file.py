import os
import shutil
import json
import random
import argparse
from sklearn.model_selection import train_test_split


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

    if not abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6:
        raise ValueError("划分比例的总和必须为1.0")

    # 使用 sklearn 的 train_test_split 两次分割数据集
    train_files, temp_files = train_test_split(
        paired_files,
        train_size=train_ratio,
        random_state=42
    )
    # 计算在临时集中的验证集比例
    relative_val_ratio = val_ratio / (val_ratio + test_ratio)
    val_files, test_files = train_test_split(
        temp_files,
        test_size=(test_ratio / (val_ratio + test_ratio)),
        random_state=42
    )

    # 创建输出文件夹并复制文件
    splits = {'train': train_files, 'val': val_files, 'test': test_files}
    for split, files in splits.items():
        split_dir = os.path.join(output_dir, split)
        os.makedirs(split_dir, exist_ok=True)
        for img, json_f in files:
            shutil.copy(os.path.join(input_dir, img), os.path.join(split_dir, img))
            shutil.copy(os.path.join(input_dir, json_f), os.path.join(split_dir, json_f))
        print(f"{split.capitalize()} 集合: 复制了 {len(files)} 对文件。")


def convert_labelme_to_coco(input_dir, output_dir):
    """
    将 Labelme JSON 转换为 COCO 格式的 labels.txt 文件，并添加 __background__ 和 __ignore__ 标签。

    参数:
    input_dir (str): 包含所有分割后的 train, val, test 文件夹的目录.
    output_dir (str): 输出 labels.txt 的目录.
    """
    label_set = set()

    # 遍历所有 split 文件夹中的 JSON 文件
    splits = ['train', 'val', 'test']
    for split in splits:
        split_dir = os.path.join(input_dir, split)
        if not os.path.exists(split_dir):
            continue
        for file in os.listdir(split_dir):
            if file.endswith('.json'):
                json_path = os.path.join(split_dir, file)
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 提取所有的标签
                    for shape in data.get('shapes', []):
                        label_set.add(shape['label'])

    # 添加 __background__ 和 __ignore__ 标签
    sorted_labels = sorted(label_set)
    sorted_labels = ['__ignore__', '__background__'] + sorted_labels

    # 写入 COCO 格式的 labels.txt
    labels_txt_path = os.path.join(output_dir, 'labels.txt')
    with open(labels_txt_path, 'w', encoding='utf-8') as f:
        for label in sorted_labels:
            f.write(f"{label}\n")

    print(f"labels.txt 已生成，包含 {len(sorted_labels)} 个标签。")


def main():
    input_path = r"E:\PJ\GIO\aiba\dataset\pose\0_net_and_sug_1800"
    output_path = r"E:\PJ\GIO\aiba\dataset\pose\0_horse\yolo\net"

    parser = argparse.ArgumentParser(description='将数据集按比例划分并生成 COCO 格式的 labels.txt 文件.')
    parser.add_argument('--input_dir', type=str, default=input_path, help='输入图像和JSON文件的文件夹')
    parser.add_argument('--output_dir', type=str, default=output_path, help='输出文件夹')
    parser.add_argument('--ratios', type=float, nargs=3, default=[0.8, 0.19, 0.01],
                        help='train, val, test 数据集的比例 (默认为 0.8, 0.19, 0.01)')
    args = parser.parse_args()

    # 验证比例之和为1
    if not abs(sum(args.ratios) - 1.0) < 1e-6:
        raise ValueError("划分比例的总和必须为1.0")

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 分割数据集
    split_dataset(args.input_dir, args.output_dir, tuple(args.ratios))

    # 转换标签为 COCO 格式
    convert_labelme_to_coco(args.output_dir, args.output_dir)


if __name__ == '__main__':
    main()
