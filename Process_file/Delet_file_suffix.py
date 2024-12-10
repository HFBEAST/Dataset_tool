import os
import sys


def delete_files_with_suffix(directory, suffixes):
    try:
        # 遍历指定目录中的所有文件
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # 检查是否是文件
            if os.path.isfile(file_path):
                file, ext = os.path.splitext(filename)
                # 检查文件名是否以指定的任意一个后缀结尾
                if any(file.endswith(suffix) for suffix in suffixes):
                    print(f"Deleting file: {file_path}")
                    os.remove(file_path)
        print("指定后缀的文件已删除。")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":

    target_directory = r"D:\23333\archive_dataset\change_back_image_daytime_fullbody"
    # 定义要删除的后缀
    suffix_list = ["__1", "__2", "__3", "__4"]
    delete_files_with_suffix(target_directory, suffix_list)
