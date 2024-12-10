import os
import shutil
import argparse


def move_json_files(source_base_dir, destination_base_dir, subfolders=None):
    """
    移动源目录下指定子文件夹中的JSON文件到目标目录对应的子文件夹中。

    :param source_base_dir: 源基础目录路径
    :param destination_base_dir: 目标基础目录路径
    :param subfolders: 要处理的子文件夹列表，默认为['train', 'test', 'val']
    """
    if subfolders is None:
        subfolders = ['train', 'test', 'val']

    for subfolder in subfolders:
        source_subdir = os.path.join(source_base_dir, subfolder)
        destination_subdir = os.path.join(destination_base_dir, subfolder)

        # 检查源子目录是否存在
        if not os.path.exists(source_subdir):
            print(f"源子目录不存在: {source_subdir}")
            continue

        # 创建目标子目录（如果不存在）
        os.makedirs(destination_subdir, exist_ok=True)

        # 遍历源子目录中的所有文件
        for filename in os.listdir(source_subdir):
            if filename.lower().endswith('.json'):
                source_file = os.path.join(source_subdir, filename)
                destination_file = os.path.join(destination_subdir, filename)

                try:
                    shutil.move(source_file, destination_file)
                    print(f"已移动: {source_file} -> {destination_file}")
                except Exception as e:
                    print(f"移动失败: {source_file} -> {destination_file}. 错误: {e}")


def parse_arguments():
    """
    解析命令行参数。
    """

    rood_path = r"E:\SUBPJ\GIO\aiba\dataset\pose\0_horse\yolo\images"
    target_path = r"E:\SUBPJ\GIO\aiba\dataset\pose\0_horse\yolo\labels"

    parser = argparse.ArgumentParser(
        description="移动train, test, val文件夹中的JSON文件到指定目标文件夹中对应的子文件夹。")
    parser.add_argument('--source', default=rood_path, type=str, help='源基础目录路径')
    parser.add_argument('--destination', default=target_path, type=str, help='目标基础目录路径')
    parser.add_argument('--folders', nargs='+', default=['train', 'test', 'val'],
                        help='要处理的子文件夹名称列表，默认是 train test val')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    move_json_files(args.source, args.destination, args.folders)
