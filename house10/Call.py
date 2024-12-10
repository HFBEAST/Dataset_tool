import rename_FILEinFOLDER
import rename_NAMEinCSV
import csv2labelme

import os

custom_name = 'g'
input_path = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\ChestnutHorseLight'

# 指定要删除的列索引（从 0 开始计数）
columns_to_delete = [9, 10, 15, 16, 19, 20, 23, 24, 31, 32, 33, 34, 41, 42]  # 替换为你需要删除的列索引列表

file_list = os.listdir(input_path)
for file in file_list:
    name, ext = os.path.splitext(file)
    if ext == '.csv':
        print(file)
        input_file = os.path.join(input_path, file)

        rename_NAMEinCSV.rename_and_replace(input_file, columns_to_delete, custom_name)

CSV_FILE = r'2333.csv'  # CSV文件路径
OUTPUT_DIR = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\img_json'  # 输出JSON文件的文件夹路径

csv2labelme.convert_csv_to_labelme(CSV_FILE, input_path, OUTPUT_DIR)



