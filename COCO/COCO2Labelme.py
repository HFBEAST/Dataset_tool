import json
import os
from collections import defaultdict


def segmentation_to_bbox(segmentation, image_width=None, image_height=None):
    """
    将COCO的segmentation（多边形）转换为边界框（bounding box）。

    参数:
        segmentation (list 或 dict): COCO格式的segmentation数据。
        image_width (int): 图片宽度（用于处理RLE格式）。
        image_height (int): 图片高度（用于处理RLE格式）。

    返回:
        list 或 None: 包含两个点的列表，分别为左上角和右下角坐标，或在无法转换时返回None。
    """
    # 处理多边形分割
    if isinstance(segmentation, list):
        if not segmentation:
            return None
        # 处理每个多边形
        # COCO的segmentation可以是多个多边形的列表，这里选择第一个有效的多边形
        for poly in segmentation:
            if not poly:
                continue
            if len(poly) < 6:  # 至少三个点
                continue
            x_coords = poly[0::2]
            y_coords = poly[1::2]
            x_min = min(x_coords)
            y_min = min(y_coords)
            x_max = max(x_coords)
            y_max = max(y_coords)
            return [[x_min, y_min], [x_max, y_max]]
        return None  # 所有多边形都无效
    # 处理RLE掩码（如果需要，可以实现）
    elif isinstance(segmentation, dict):
        # 如果需要处理RLE格式，可以在这里实现
        # 这里我们选择跳过RLE格式的注释
        return None
    else:
        return None


def convert_coco_to_labelme(coco_json_path, output_dir, images_dir):
    """
    将COCO格式的JSON文件转换为LabelMe格式的JSON文件（使用边界框）。

    参数:
        coco_json_path (str): COCO格式JSON文件的路径。
        output_dir (str): 保存LabelMe格式JSON文件的目录。
        images_dir (str): 图片文件夹的路径，用于删除相关图片。
    """
    # 读取COCO JSON文件
    with open(coco_json_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)

    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    # 创建类别ID到名称的映射
    categories = {cat['id']: cat['name'] for cat in coco_data.get('categories', [])}

    # 创建图片ID到图片信息的映射，过滤掉无效的图片
    images = {}
    for img in coco_data.get('images', []):
        if not isinstance(img, dict):
            continue
        required_fields = ['id', 'file_name', 'width', 'height']
        if all(field in img for field in required_fields):
            images[img['id']] = img
        else:
            print(f"跳过无效的图片信息: {img}")

    # 创建图片ID到注释列表的映射
    annotations = defaultdict(list)
    for ann in coco_data.get('annotations', []):
        if not isinstance(ann, dict):
            continue
        image_id = ann.get('image_id')
        if image_id in images:
            annotations[image_id].append(ann)
        else:
            print(f"跳过与无效图片ID关联的注释: {ann}")

    # 遍历每张图片并生成LabelMe格式的JSON
    for image_id, img in images.items():
        file_name = img['file_name']
        width = img['width']
        height = img['height']
        image_path = os.path.join(images_dir, file_name)

        # 获取与该图片对应的所有注释
        anns = annotations.get(image_id, [])

        shapes = []
        for ann in anns:
            segmentation = ann.get('segmentation', [])
            try:
                # 尝试转换segmentation为边界框
                bbox = segmentation_to_bbox(segmentation)
                if bbox is None:
                    print(f"跳过无法转换的segmentation: {segmentation} in annotation ID {ann.get('id')}")
                    continue  # 跳过无法转换的注释
            except KeyError as e:
                # 打印出错信息并删除相关图片
                print(f"错误的segmentation: {segmentation} in annotation ID {ann.get('id')}")
                print(f"KeyError: {e}")
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"删除图片: {image_path} 因为segmentation有问题")
                else:
                    print(f"图片文件不存在，无法删除: {image_path}")
                continue  # 跳过该注释

            category_id = ann.get('category_id')
            label = categories.get(category_id, 'undefined')

            shape = {
                "label": label,  # 从categories的name提取
                "points": bbox,
                "group_id": None,
                "description": "",
                "shape_type": "rectangle",
                "flags": {}
            }
            shapes.append(shape)

        # 如果没有有效的shapes，跳过生成JSON文件
        if not shapes:
            print(f"没有有效的shape, 跳过生成: {file_name}")
            continue

        # 生成LabelMe格式的JSON数据
        labelme_json = {
            "version": "5.5.0",
            "flags": {},
            "shapes": shapes,
            "imagePath": file_name,
            "imageData": None,
            "imageHeight": height,
            "imageWidth": width
        }

        # 定义JSON文件的保存路径
        json_file_name = os.path.splitext(file_name)[0] + '.json'
        json_file_path = os.path.join(output_dir, json_file_name)

        # 保存JSON文件
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(labelme_json, json_file, ensure_ascii=False, indent=4)

        print(f"已保存: {json_file_path}")

    # 获取图片和JSON文件夹中的文件名
    image_files = set(f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')))
    json_files = set(f for f in os.listdir(output_dir) if f.lower().endswith('.json'))

    # 比较并删除没有对应文件的情况
    for img_file in image_files:
        json_file_name = os.path.splitext(img_file)[0] + '.json'
        if json_file_name not in json_files:
            img_path = os.path.join(images_dir, img_file)
            os.remove(img_path)
            print(f"删除图片: {img_path} 因为没有对应的JSON文件")

    for json_file in json_files:
        img_file_name = os.path.splitext(json_file)[0] + '.jpg'  # 这里假设图片为jpg格式
        if img_file_name not in image_files:
            json_path = os.path.join(output_dir, json_file)
            os.remove(json_path)
            print(f"删除JSON文件: {json_path} 因为没有对应的图片文件")


if __name__ == "__main__":
    # 示例用法
    coco_json_path = r'H:\DATASET\COCO_horse\annotations\train2017_horse.json'  # 替换为你的COCO JSON文件路径
    output_dir = r'H:\DATASET\COCO_horse\train'  # 替换为你想保存LabelMe JSON文件的目录
    images_dir = r'H:\DATASET\COCO_horse\train'  # 替换为你的图片文件夹路径

    convert_coco_to_labelme(coco_json_path, output_dir, images_dir)
