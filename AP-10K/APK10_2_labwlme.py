import json
import os
import base64

# COCO 到 LabelMe 的关键点名称映射
COCO_TO_LABELME_KEYPOINTS = {
    "left_eye": "L_Eye",
    "right_eye": "R_Eye",
    "nose": "Nose",
    "neck": "Throat",
    "root_of_tail": "TailBase",
    "left_shoulder": "L_F_Elbow",
    "left_elbow": "L_F_Knee",
    "left_front_paw": "L_F_Paw",
    "right_shoulder": "R_F_Elbow",
    "right_elbow": "R_F_Knee",
    "right_front_paw": "R_F_Paw",
    "left_hip": "L_B_Elbow",
    "left_knee": "L_B_Knee",
    "left_back_paw": "L_B_Paw",
    "right_hip": "R_B_Elbow",
    "right_knee": "R_B_Knee",
    "right_back_paw": "R_B_Paw"
}


def convert_coco_to_labelme(coco_json_path, images_dir, output_dir):
    # 读取 COCO 格式的 JSON 文件
    with open(coco_json_path, 'r', encoding='utf-8') as f:
        coco = json.load(f)

    # 创建类别 ID 到类别信息的映射
    categories = {cat['id']: cat for cat in coco['categories']}

    # 创建图像 ID 到图像信息的映射
    images = {img['id']: img for img in coco['images']}

    # 创建图像 ID 到其标注的映射
    annotations_map = {}
    for ann in coco['annotations']:
        image_id = ann['image_id']
        if image_id not in annotations_map:
            annotations_map[image_id] = []
        annotations_map[image_id].append(ann)

    # 如果输出目录不存在，则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历每个图像并生成对应的 LabelMe JSON 文件
    for image_id, img in images.items():
        labelme_json = {
            "version": "5.5.0",  # 根据您的示例更新版本
            "flags": {},
            "shapes": [],
            "imagePath": img['file_name'],
            "imageData": None,  # 如果不需要嵌入图像数据，可以保持为空
            "imageHeight": img['height'],
            "imageWidth": img['width']
        }

        image_path = os.path.join(images_dir, img['file_name'])
        if os.path.exists(image_path):
            with open(image_path, 'rb') as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                labelme_json["imageData"] = encoded
        else:
            print(f"图像文件 {image_path} 不存在。")

        if image_id in annotations_map:
            for ann in annotations_map[image_id]:
                category_id = ann['category_id']
                category = categories.get(category_id, {})
                label = category.get('name', 'undefined')

                # 使用边界框创建矩形形状
                bbox = ann.get('bbox', [])
                if len(bbox) == 4:
                    x, y, width, height = bbox
                    shape = {
                        "label": label,
                        "points": [
                            [x, y],
                            [x + width, y + height]
                        ],
                        "group_id": None,
                        "shape_type": "rectangle",
                        "flags": {}
                    }
                    labelme_json["shapes"].append(shape)

                # 如果存在关键点，则将其作为单独的点添加
                keypoints = ann.get('keypoints', [])
                num_keypoints = ann.get('num_keypoints', 0)
                if keypoints and num_keypoints > 0:
                    # 获取关键点名称列表
                    keypoint_names = category.get('keypoints', [])

                    if not keypoint_names:
                        print(f"类别 '{label}' 没有定义 'keypoints'，跳过关键点标注。")
                        continue

                    for i in range(num_keypoints):
                        if i >= len(keypoint_names):
                            print(f"关键点索引 {i} 超出类别 '{label}' 的 'keypoints' 列表范围。")
                            break
                        coco_kp_name = keypoint_names[i]
                        kp_label = COCO_TO_LABELME_KEYPOINTS.get(coco_kp_name, f"{label}_keypoint_{i}")

                        x_kp = keypoints[3 * i]
                        y_kp = keypoints[3 * i + 1]
                        v = keypoints[3 * i + 2]
                        if v > 0:
                            point_shape = {
                                "label": kp_label,
                                "points": [[x_kp, y_kp]],
                                "group_id": None,
                                "shape_type": "point",
                                "flags": {}
                            }
                            labelme_json["shapes"].append(point_shape)

        # 保存 LabelMe JSON 文件
        output_path = os.path.join(output_dir, os.path.splitext(img['file_name'])[0] + '.json')
        with open(output_path, 'w', encoding='utf-8') as out_file:
            json.dump(labelme_json, out_file, ensure_ascii=False, indent=4)

        print(f"已转换 {img['file_name']} 至 {output_path}")


if __name__ == "__main__":
    # 替换为您的文件路径
    coco_json_path = r'E:\SUBPJ\GIO\aiba\dataset\ap-10k\ap-10k\annotations\1\9.json'  # 输入的标注 JSON 文件路径
    images_dir = r'E:\SUBPJ\GIO\aiba\dataset\ap-10k\ap-10k\img'  # 图像文件所在目录
    output_dir = r'E:\SUBPJ\GIO\aiba\dataset\ap-10k\ap-10k\img'  # 输出 LabelMe JSON 文件的目录

    convert_coco_to_labelme(coco_json_path, images_dir, output_dir)
