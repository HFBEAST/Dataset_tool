import os
import shutil

def move_file(files, ):
    for file in files:
        print(file)
        source_file = os.path.join(root, file)
        target_file = os.path.join(target_dir, file)

        # 如果目标文件已存在，添加编号以避免覆盖
        if os.path.exists(target_file):
            base, extension = os.path.splitext(file)
            count = 1
            while True:
                new_file = f"{base}_{count}{extension}"
                new_target = os.path.join(target_dir, new_file)
                if not os.path.exists(new_target):
                    target_file = new_target
                    break
                count += 1

        try:
            shutil.copy(source_file, target_file)
            print(f"已移动: {source_file} -> {target_file}")
        except Exception as e:
            print(f"移动文件失败: {source_file}. 错误: {e}")


def move_all_files(source_dir, target_dir):
    """
    将source_dir中所有子文件夹的文件移动到target_dir中。

    :param source_dir: 源文件夹路径
    :param target_dir: 目标文件夹路径
    """
    if not os.path.exists(source_dir):
        print(f"源文件夹不存在: {source_dir}")
        return

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"已创建目标文件夹: {target_dir}")

    # 遍历源文件夹中的所有子文件夹和文件
    for root, dirs, files in os.walk(source_dir):
        print(dirs)
        for file in files:
            print(file)
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_dir, file)

            # 如果目标文件已存在，添加编号以避免覆盖
            if os.path.exists(target_file):
                base, extension = os.path.splitext(file)
                count = 1
                while True:
                    new_file = f"{base}_{count}{extension}"
                    new_target = os.path.join(target_dir, new_file)
                    if not os.path.exists(new_target):
                        target_file = new_target
                        break
                    count += 1

            try:
                shutil.copy(source_file, target_file)
                print(f"已移动: {source_file} -> {target_file}")
            except Exception as e:
                print(f"移动文件失败: {source_file}. 错误: {e}")

    print("所有文件已移动完成。")

if __name__ == "__main__":
    # 示例用法
    source_directory = r"E:\PJ\GIO\aiba\dataset\pose\0_net_and_sug_1800"  # 源文件夹路径
    target_directory = r"E:\PJ\GIO\aiba\dataset\pose\1_net_1600_aiba_3200"  # 目标文件夹路径

    move_all_files(source_directory, target_directory)
