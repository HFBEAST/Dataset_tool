import os
import shutil

# 定义源文件夹和目标文件夹路径
source_folder = r"H:\0_program\My_learn\mmlab\mmpose\data\animalpose\PASCAL2011_animal_annotation\2333"
target_folder = r"H:\0_program\My_learn\mmlab\mmpose\data\animalpose\VOC2012\JPEGImages"
output_folder = r"H:\0_program\My_learn\mmlab\mmpose\data\animalpose\PASCAL2011_animal_annotation\2333"

# 获取源文件夹中所有文件的名字（不包括后缀）
source_filenames = set(os.path.splitext(file)[0] for file in os.listdir(source_folder) if
                       os.path.isfile(os.path.join(source_folder, file)))

# 遍历目标文件夹中的文件，找到与源文件夹中相同名字的照片并复制到输出文件夹
for file in os.listdir(target_folder):
    file_path = os.path.join(target_folder, file)
    file_name, file_ext = os.path.splitext(file)

    # 如果文件名在源文件夹中存在且是图片文件，则复制到输出文件夹
    if file_name in source_filenames and file_ext.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        shutil.copy(file_path, output_folder)
        print(f"Copied: {file} to {output_folder}")

print("复制完成！")