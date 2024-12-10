import os
import glob
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_visible_bounds_attributes(visible_bounds):
    """
    重命名visible_bounds中的属性：
    - xmax -> ymin
    - height -> xmax
    - width -> ymax
    """
    # 使用临时变量保存原始属性的值
    xmax_value = visible_bounds.get('xmax')
    height_value = visible_bounds.get('height')
    width_value = visible_bounds.get('width')

    # 重命名属性
    if xmax_value is not None:
        visible_bounds.set('ymin', xmax_value)
        del visible_bounds.attrib['xmax']
    if height_value is not None:
        visible_bounds.set('xmax', height_value)
        del visible_bounds.attrib['height']
    if width_value is not None:
        visible_bounds.set('ymax', width_value)
        del visible_bounds.attrib['width']


def update_visible_bounds(visible_bounds, max_x, max_y):
    """
    更新visible_bounds中的xmax和ymax属性为最大x和最大y值
    """
    visible_bounds.set('xmax', str(max_x))
    visible_bounds.set('ymax', str(max_y))

def process_xml_file(xml_file, output_folder):
    """
    处理单个XML文件，按照要求修改并保存到输出文件夹
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"解析XML文件时出错: {xml_file}\n错误信息: {e}")
        return

    # 找到visible_bounds元素
    visible_bounds = root.find('visible_bounds')
    if visible_bounds is None:
        print(f"在文件 {xml_file} 中未找到 <visible_bounds> 元素，跳过。")
        return

    # 重命名属性
    rename_visible_bounds_attributes(visible_bounds)

    # 收集所有keypoints的x和y值
    keypoints = root.find('keypoints')
    if keypoints is None:
        print(f"在文件 {xml_file} 中未找到 <keypoints> 元素，跳过。")
        return

    x_values = []
    y_values = []
    for keypoint in keypoints.findall('keypoint'):
        x = keypoint.get('x')
        y = keypoint.get('y')
        if x is not None and y is not None:
            try:
                x = float(x)
                y = float(y)
                x_values.append(x)
                y_values.append(y)
            except ValueError:
                print(f"在文件 {xml_file} 的关键点中发现非数字的x或y值，跳过该关键点。")
                continue

    if not x_values or not y_values:
        print(f"在文件 {xml_file} 的关键点中未找到有效的x或y值，跳过。")
        return

    max_x = max(x_values)
    max_y = max(y_values)

    # 更新visible_bounds中的xmax和ymax
    update_visible_bounds(visible_bounds, max_x, max_y)

    # 保存修改后的XML到输出文件夹
    base_name = os.path.basename(xml_file)
    output_path = os.path.join(output_folder, base_name)
    try:
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"已处理并保存: {output_path}")
    except IOError as e:
        print(f"保存修改后的XML文件时出错: {output_path}\n错误信息: {e}")

def batch_modify_xml(input_folder, output_folder):
    """
    批量处理输入文件夹中的所有XML文件，并保存到输出文件夹
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    xml_files = glob.glob(os.path.join(input_folder, '*.xml'))
    if not xml_files:
        print("在指定的文件夹中未找到任何XML文件。")
        return

    for xml_file in xml_files:
        process_xml_file(xml_file, output_folder)

def select_folder(title):
    """
    使用tkinter的文件夹选择对话框让用户选择文件夹
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    folder_selected = filedialog.askdirectory(title=title)
    return folder_selected

def main(input_folder,output_folder):

    # 执行批量修改
    batch_modify_xml(input_folder, output_folder)

    # 完成提示
    messagebox.showinfo("完成", "所有XML文件已成功修改并保存到输出文件夹。")

if __name__ == "__main__":
    input_folder = r"D:\23333\archive\animalpose\animalpose_anno2\horse"
    output_folder = r"H:\DATASET\horses\horses200"

    main(input_folder, output_folder)
