import os
import json
import shutil
import xmltodict
from PIL import Image
import base64

def convert_xml_to_json(image_folder, xml_folder, output_folder):
    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 定义 XML 到 JSON 的标签映射
    label_mapping = {
        "L_eye": "L_Eye",
        "R_eye": "R_Eye",
        "L_ear": "L_EarBase",
        "R_ear": "R_EarBase",
        "Nose": "Nose",
        "Throat": "Throat",
        "Tail": "TailBase",
        "withers": "Withers",
        "L_F_elbow": "L_F_Elbow",
        "R_F_elbow": "R_F_Elbow",
        "L_B_elbow": "L_B_Elbow",
        "R_B_elbow": "R_B_Elbow",
        "L_F_knee": "L_F_Knee",
        "R_F_knee": "R_F_Knee",
        "L_B_knee": "L_B_Knee",
        "R_B_knee": "R_B_Knee",
        "L_F_paw": "L_F_Paw",
        "R_F_paw": "R_F_Paw",
        "L_B_paw": "L_B_Paw",
        "R_B_paw": "R_B_Paw"
    }

    # 遍历 XML 文件夹中的所有 XML 文件
    for xml_file in os.listdir(xml_folder):
        if not xml_file.endswith('.xml'):
            continue  # 跳过非 XML 文件

        xml_path = os.path.join(xml_folder, xml_file)
        try:
            with open(xml_path, 'r', encoding='utf-8') as xf:
                xml_content = xf.read()
            data_dict = xmltodict.parse(xml_content)
        except Exception as e:
            print(f"错误: 解析 XML 文件 {xml_file} 时出错: {e}")
            continue

        # 提取必要信息
        annotation = data_dict.get('annotation')
        if not annotation:
            print(f"警告: XML 文件 {xml_file} 中缺少 <annotation> 标签，跳过此文件。")
            continue

        image_name = annotation.get('image')
        if not image_name:
            print(f"警告: XML 文件 {xml_file} 中缺少 <image> 标签，跳过此文件。")
            continue

        base_name = os.path.splitext(image_name)[0]
        new_image_name = base_name + '.jpg'
        image_src_path = os.path.join(image_folder, image_name)
        image_dst_path = os.path.join(output_folder, new_image_name)

        # 检查图片是否存在
        if not os.path.exists(image_src_path):
            print(f"警告: 图片文件 {image_src_path} 不存在，跳过此 XML 文件。")
            continue

        # 复制并转换图片为 JPEG 格式
        try:
            with Image.open(image_src_path) as img:
                img = img.convert("RGB")  # 确保是 RGB 模式
                img.save(image_dst_path, "JPEG")
        except Exception as e:
            print(f"错误: 处理图片 {image_src_path} 时出错: {e}")
            continue

        # 获取图片尺寸
        try:
            with Image.open(image_dst_path) as img:
                width, height = img.size
        except Exception as e:
            print(f"错误: 获取图片尺寸 {image_dst_path} 时出错: {e}")
            width, height = 0, 0

        # 读取图片数据并进行 base64 编码
        try:
            with open(image_dst_path, 'rb') as img_f:
                image_data = base64.b64encode(img_f.read()).decode('utf-8')
        except Exception as e:
            print(f"错误: 读取图片数据 {image_dst_path} 时出错: {e}")
            image_data = ""

        # 构建 JSON 结构
        json_dict = {
            "version": "5.5.0",
            "flags": {},
            "shapes": [],
            "imagePath": new_image_name,
            "imageData": image_data,
            "imageHeight": height,
            "imageWidth": width
        }

        # 添加类别的矩形框（可见边界）
        category = annotation.get('category')
        visible_bounds = annotation.get('visible_bounds')
        if category and visible_bounds:
            try:
                xmin = float(visible_bounds.get('@xmin', 0))
                ymin = float(visible_bounds.get('@ymin', 0))
                xmax = float(visible_bounds.get('@xmax', 0))
                ymax = float(visible_bounds.get('@ymax', 0))
                rectangle_shape = {
                    "label": category.strip(),
                    "points": [
                        [xmin, ymin],
                        [xmax, ymax]
                    ],
                    "group_id": None,
                    "shape_type": "rectangle",
                    "flags": {}
                }
                json_dict["shapes"].append(rectangle_shape)
            except ValueError as ve:
                print(f"警告: XML 文件 {xml_file} 中 visible_bounds 有无效的数值: {ve}")

        # 处理关键点
        keypoints = annotation.get('keypoints', {}).get('keypoint', [])
        if isinstance(keypoints, dict):
            keypoints = [keypoints]  # 转换为列表

        for kp in keypoints:
            visible = kp.get('@visible')
            if visible != "1":
                continue  # 跳过不可见的关键点

            label_xml = kp.get('@name')
            if not label_xml:
                print(f"警告: XML 文件 {xml_file} 中存在没有名称的关键点，跳过此关键点。")
                continue

            # 根据映射表转换标签名称
            label_json = label_mapping.get(label_xml)
            if not label_json:
                print(f"警告: XML 文件 {xml_file} 中关键点名称 '{label_xml}' 不在映射表中，跳过此关键点。")
                continue

            try:
                x = float(kp.get('@x', 0))
                y = float(kp.get('@y', 0))
            except ValueError as ve:
                print(f"警告: XML 文件 {xml_file} 中关键点 {label_xml} 有无效的坐标: {ve}")
                continue

            if label_json:
                point_shape = {
                    "label": label_json.strip(),
                    "points": [
                        [x, y]
                    ],
                    "group_id": None,
                    "shape_type": "point",
                    "flags": {}
                }
                json_dict["shapes"].append(point_shape)

        # 保存 JSON 文件
        json_file_name = base_name + '.json'
        json_path = os.path.join(output_folder, json_file_name)
        try:
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(json_dict, jf, ensure_ascii=False, indent=4)
            print(f"已转换: {xml_file} -> {json_file_name}")
        except Exception as e:
            print(f"错误: 保存 JSON 文件 {json_file_name} 时出错: {e}")


if __name__ == "__main__":

    image_folder = r"H:\DATASET\horses\horses200_xml"
    xml_folder = r"H:\DATASET\horses\horses200_xml"
    output_folder = r"H:\DATASET\horses\horses200_labelme"

    convert_xml_to_json(image_folder, xml_folder, output_folder)
