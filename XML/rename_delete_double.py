import os

def rename_files_in_directory(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹 '{folder_path}' 不存在！")
        return

    # 获取文件夹中的所有文件
    files = os.listdir(folder_path)
    for file_name in files:
        # 获取文件的完整路径
        full_path = os.path.join(folder_path, file_name)

        # 如果是文件而不是文件夹
        if os.path.isfile(full_path):
            # 分离文件名和扩展名
            base_name, ext = os.path.splitext(file_name)

            # 找到最后一个'_'的位置
            last_underscore_index = base_name.rfind('_')

            # 如果找到了'_'，则进行重命名
            if last_underscore_index != -1:
                # 从后往前到第一个'_'（包括'_'）的内容全部删除
                new_base_name = base_name[:last_underscore_index]
                new_file_name = new_base_name + ext

                # 重命名文件，如果目标文件已存在则删除目标文件
                new_full_path = os.path.join(folder_path, new_file_name)
                if os.path.exists(new_full_path):
                    os.remove(new_full_path)
                os.rename(full_path, new_full_path)
                print(f"已重命名: {file_name} -> {new_file_name}")
            else:
                print(f"跳过文件（无'_'）：{file_name}")

if __name__ == "__main__":
    # 指定要处理的文件夹路径
    folder_path = r"H:\0_program\My_learn\mmlab\mmpose\data\animalpose\PASCAL2011_animal_annotation\horse"
    rename_files_in_directory(folder_path)