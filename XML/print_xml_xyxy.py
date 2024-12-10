import os
import cv2
import xml.etree.ElementTree as ET


def draw_annotations(image, annotation):
    """
    在图像上绘制边框和关键点。

    :param image: 要绘制的图像
    :param annotation: 解析后的XML注释对象
    :return: 绘制后的图像
    """
    # 绘制边框
    visible_bounds = annotation.find('visible_bounds')
    xmin = int(float(visible_bounds.get('xmin')))
    ymin = int(float(visible_bounds.get('ymin')))
    xmax = int(float(visible_bounds.get('xmax')))
    ymax = int(float(visible_bounds.get('ymax')))
    cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)  # 绿色边框

    # 绘制关键点
    keypoints = annotation.find('keypoints')
    for kp in keypoints.findall('keypoint'):
        visible = kp.get('visible')
        if visible == "1":
            x = int(float(kp.get('x')))
            y = int(float(kp.get('y')))
            name = kp.get('name')
            # 绘制圆点
            cv2.circle(image, (x, y), 3, (0, 0, 255), -1)  # 红色圆点
            # 绘制标签
            cv2.putText(image, name, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.4, (255, 0, 0), 1, cv2.LINE_AA)  # 蓝色文字
    return image


def process_single_file(xml_file, input_img_folder, output_img_folder):
    """
    处理单个XML文件，绘制标注并保存图像。

    :param xml_file: XML文件路径
    :param input_img_folder: 输入图像文件夹路径
    :param output_img_folder: 输出图像文件夹路径
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        image_name = root.find('image').text
        image_path = os.path.join(input_img_folder, image_name)

        if not os.path.exists(image_path):
            print(f"图像文件不存在: {image_path}")
            return

        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像文件: {image_path}")
            return

        annotated_image = draw_annotations(image, root)

        # 确保输出文件夹存在
        os.makedirs(output_img_folder, exist_ok=True)
        output_path = os.path.join(output_img_folder, image_name)
        cv2.imwrite(output_path, annotated_image)
        print(f"已保存标注图像: {output_path}")

    except ET.ParseError as e:
        print(f"解析XML文件失败: {xml_file}, 错误: {e}")
    except Exception as e:
        print(f"处理文件时出错: {xml_file}, 错误: {e}")


def main(input_img_folder, input_xml_folder, output_img_folder):
    """
    主函数，处理输入文件夹中的所有XML文件。

    :param input_img_folder: 输入图像文件夹路径
    :param input_xml_folder: 输入XML文件夹路径
    :param output_img_folder: 输出图像文件夹路径
    """
    # 获取所有XML文件
    xml_files = [f for f in os.listdir(input_xml_folder) if f.endswith('.xml')]

    if not xml_files:
        print(f"在文件夹中未找到XML文件: {input_xml_folder}")
        return

    for xml_file in xml_files:
        xml_path = os.path.join(input_xml_folder, xml_file)
        process_single_file(xml_path, input_img_folder, output_img_folder)


if __name__ == "__main__":
    input_xml_folder = r"H:\DATASET\horses\print_xml"
    input_img_folder = r"H:\DATASET\horses\horses200"
    output_img_folder = r"H:\DATASET\horses\print_xml"

    main(input_img_folder, input_xml_folder, output_img_folder)
