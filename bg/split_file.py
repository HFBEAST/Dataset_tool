import os
import shutil
import argparse
import random
from pathlib import Path


def parse_arguments():
    parser = argparse.ArgumentParser(description="将图片按指定比例分配到train、val、test文件夹中。")
    parser.add_argument(
        '--source_dir',
        type=str,
        default=r"E:\PJ\GIO\aiba\dataset\no_horse\sum",
        help='源图片文件夹路径。'
    )
    parser.add_argument(
        '--output_dir',
        default=r"E:\PJ\GIO\aiba\dataset\no_horse\horse_bg",
        type=str,
        help='输出文件夹路径。将创建train、val、test子文件夹。'
    )
    parser.add_argument(
        '--train_ratio',
        type=float,
        default=0.8,
        help='训练集比例，默认为0.8。'
    )
    parser.add_argument(
        '--val_ratio',
        type=float,
        default=0.19,
        help='验证集比例，默认为0.19。'
    )
    parser.add_argument(
        '--test_ratio',
        type=float,
        default=0.01,
        help='测试集比例，默认为0.01。'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='随机种子，确保可重复性。默认为42。'
    )
    return parser.parse_args()


def get_image_files(source_dir):
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif')
    image_files = [f for f in os.listdir(source_dir) if f.lower().endswith(supported_extensions)]
    return image_files


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def split_data(image_files, train_ratio, val_ratio, test_ratio, seed=42):
    random.seed(seed)
    random.shuffle(image_files)
    total = len(image_files)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    train_files = image_files[:train_end]
    val_files = image_files[train_end:val_end]
    test_files = image_files[val_end:]
    return train_files, val_files, test_files


def copy_files(files, source_dir, dest_dir):
    for file in files:
        src = os.path.join(source_dir, file)
        dst = os.path.join(dest_dir, file)
        shutil.copy2(src, dst)


def main():
    args = parse_arguments()

    source_dir = args.source_dir
    output_dir = args.output_dir
    train_ratio = args.train_ratio
    val_ratio = args.val_ratio
    test_ratio = args.test_ratio
    seed = args.seed

    # 检查比例之和是否为1
    total_ratio = train_ratio + val_ratio + test_ratio
    if not abs(total_ratio - 1.0) < 1e-6:
        print(f"错误：训练集、验证集和测试集的比例之和必须为1。当前总和为 {total_ratio}")
        return

    # 获取所有图片文件
    image_files = get_image_files(source_dir)
    if not image_files:
        print(f"在源文件夹中未找到支持的图片文件: {source_dir}")
        return

    print(f"找到 {len(image_files)} 张图片。开始分割数据集...")

    # 分割数据
    train_files, val_files, test_files = split_data(
        image_files,
        train_ratio,
        val_ratio,
        test_ratio,
        seed
    )

    print(f"训练集: {len(train_files)} 张图片")
    print(f"验证集: {len(val_files)} 张图片")
    print(f"测试集: {len(test_files)} 张图片")

    # 创建目标子文件夹
    train_dir = os.path.join(output_dir, 'train')
    val_dir = os.path.join(output_dir, 'val')
    test_dir = os.path.join(output_dir, 'test')

    create_dir(train_dir)
    create_dir(val_dir)
    create_dir(test_dir)

    # 复制文件
    copy_files(train_files, source_dir, train_dir)
    copy_files(val_files, source_dir, val_dir)
    copy_files(test_files, source_dir, test_dir)

    print(f"数据集分割完成。文件已复制到 {output_dir}")


if __name__ == "__main__":
    main()
