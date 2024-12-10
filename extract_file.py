import os
import shutil

def copy_files_with_interval(source_folder, target_folder, interval):
    # 确保源文件夹和目标文件夹存在
    if not os.path.exists(source_folder):
        print(f"源文件夹 '{source_folder}' 不存在。")
        return
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 获取源文件夹中所有文件
    files = os.listdir(source_folder)
    files.sort()  # 对文件进行排序，以确保复制顺序一致

    # 遍历文件并按指定间隔复制
    for i in range(0, len(files), interval):
        file_to_copy = files[i]
        source_file_path = os.path.join(source_folder, file_to_copy)
        target_file_path = os.path.join(target_folder, file_to_copy)

        # 仅复制文件，跳过文件夹
        if os.path.isfile(source_file_path):
            shutil.copy2(source_file_path, target_file_path)
            print(f"已复制: {file_to_copy}")

if __name__ == "__main__":
    source_folder = "source_folder_path"  # 替换为你的源文件夹路径
    target_folder = "target_folder_path"  # 替换为你的目标文件夹路径
    interval = 3  # 每隔多少个文件复制一次

    copy_files_with_interval(source_folder, target_folder, interval)