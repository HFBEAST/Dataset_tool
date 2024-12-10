import os
import json

pose_point_categories = {
    "categories": [
        {
            "supercategory": "animal",
            "id": 1,
            "name": "animal",
            "keypoints": [
                "L_Eye",
                "R_Eye",
                "L_EarBase",
                "R_EarBase",
                "Nose",
                "Throat",
                "TailBase",
                "Withers",
                "L_F_Elbow",
                "R_F_Elbow",
                "L_B_Elbow",
                "R_B_Elbow",
                "L_F_Knee",
                "R_F_Knee",
                "L_B_Knee",
                "R_B_Knee",
                "L_F_Paw",
                "R_F_Paw",
                "L_B_Paw",
                "R_B_Paw"
            ],
            "skeleton": [
                [1, 2], [1, 3], [2, 4], [1, 5], [2, 5], [5, 6], [6, 8],
                [7, 8], [6, 9], [9, 13], [13, 17], [6, 10], [10, 14], [14, 18],
                [7, 11], [11, 15], [15, 19], [7, 12], [12, 16], [16, 20]
            ]
        }
    ]
}

class LabelMe2COCO:
    def __init__(self, labelme_folder, save_json_path, pose_point_categories):
        self.labelme_folder = labelme_folder
        self.save_json_path = save_json_path
        self.pose_point_categories = pose_point_categories
        self.key_points_list = pose_point_categories["categories"][0]["keypoints"]

        self.images = []
        self.annotations = []
        self.ann_id = 1
        self.image_id = 1
        self.height = 0
        self.width = 0

        json_files_list = self.get_json_list(self.labelme_folder)
        self.labelme_files_list = json_files_list

    def image_info(self, data):
        # 处理图片信息
        image_info = {
            'id': self.image_id,
            'file_name': data['imagePath'],
            'height': data['imageHeight'],
            'width': data['imageWidth']
        }
        self.image_id += 1
        return image_info

    def data2coco(self):
        for file_path in self.labelme_files_list:
            print(f'Processing {file_path}...')
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.images.append(self.image_info(data))
                self.annotations.append(self.process_annotations(data))

    def process_annotations(self, data):
        keypoints = self.get_keypoints(data)
        bbox = self.calculate_bbox(data)

        annotation = {
            'keypoints': keypoints,
            'image_id': self.image_id - 1,  # 当前图像ID
            'id': self.ann_id - 1,
            'num_keypoints': sum([1 for i in range(0, len(keypoints), 3) if keypoints[i] != 0]),
            'bbox': bbox,
            'iscrowd': 0,
            'area': bbox[2] * bbox[3],  # 面积为宽度 * 高度
            'category_id': 1  # 假设所有的关键点都属于类别 1 (动物)
        }

        self.ann_id += 1
        return annotation

    def get_keypoints(self, data):
        keypoints_coco_format = []
        for point_name in self.key_points_list:
            found = False
            for shape in data.get('shapes', []):
                if shape['label'] == point_name:
                    x, y = shape['points'][0]
                    keypoints_coco_format.extend([x, y, 2.0])
                    found = True
                    break
            if not found:
                keypoints_coco_format.extend([0.0, 0.0, 0.0])
        return keypoints_coco_format

    def calculate_bbox(self, data):
        # 找到 'rectangle' 类型的形状，并计算边界框
        for shape in data.get('shapes', []):
            if shape['shape_type'] == 'rectangle':
                x_min, y_min = shape['points'][0]
                x_max, y_max = shape['points'][1]
                width = x_max - x_min
                height = y_max - y_min
                return [x_min, y_min, width, height]
        return [0.0, 0.0, 0.0, 0.0]  # 如果没有找到 'rectangle' 返回空边界框

    def get_json_list(self, json_dir):
        target_extension = '.json'
        abs_filepath_list = []
        for root, dirs, files in os.walk(json_dir):
            for file in files:
                if file.endswith(target_extension):
                    abs_filepath = os.path.join(root, file)
                    abs_filepath_list.append(abs_filepath)
        return abs_filepath_list

    def save_json(self):
        # 生成COCO格式的数据
        coco_format = {
            "info": {
                "description": "AnimalPose dataset Generated by MMPose Team",
                "version": "1.0",
                "year": "2021",
                "date_created": "2021/04/25"
            },
            "images": self.images,
            "annotations": self.annotations,
            "categories": self.pose_point_categories['categories']
        }

        # 保存为JSON文件
        with open(self.save_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(coco_format, json_file, ensure_ascii=False, indent=4)
        print(f"COCO format JSON saved at {self.save_json_path}")


def convert(total_data_dir, annotations_dir, pose_point_categories):
    convert_list = ['train', 'test', 'val']  # 需要处理的三个文件夹
    for folder in convert_list:
        folder_path = os.path.join(total_data_dir, folder)
        if not os.path.exists(folder_path):
            continue

        save_json_path = os.path.join(annotations_dir, f'horse_{folder}.json')
        print(f'Converting {folder_path} to {save_json_path}...')
        convert_file = LabelMe2COCO(labelme_folder=folder_path, save_json_path=save_json_path, pose_point_categories=pose_point_categories)

        convert_file.data2coco()  # 处理文件夹中的所有json文件
        convert_file.save_json()  # 保存生成的COCO格式json
        print(f'Converted {folder_path} to {save_json_path} successfully.')


def main(total_data_dir, pose_point_categories):
    annotations_dir = os.path.join(total_data_dir, 'annotations')
    if not os.path.exists(annotations_dir):
        os.makedirs(annotations_dir)

    convert(total_data_dir, annotations_dir, pose_point_categories)


if __name__ == '__main__':
    total_data_dir = r'E:\PJ\GIO\aiba\dataset\pose\0_horse\mmpose\net_1800_aiba_3200'  # 替换为你的数据总目录路径
    main(total_data_dir, pose_point_categories)