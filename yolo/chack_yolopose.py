import os
import cv2

# 配置参数
IMAGE_DIR = r'E:\SUBPJ\GIO\aiba\dataset\pose\0_horse\yolo\images\test'         # 图像目录
ANNOTATION_DIR = r'E:\SUBPJ\GIO\aiba\dataset\pose\0_horse\yolo\labels\test'  # 标注文件目录
OUTPUT_DIR = r'E:\SUBPJ\GIO\aiba\dataset\pose\0_horse\yolo\check'        # 输出目录

# 创建输出目录（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 定义20个关键点的名称
KEYPOINT_NAMES = [
    "L_Eye", "R_Eye", "L_EarBase", "R_EarBase", "Nose", "Throat",
    "TailBase", "Withers", "L_F_Elbow", "R_F_Elbow",
    "L_B_Elbow", "R_B_Elbow", "L_F_Knee", "R_F_Knee",
    "L_B_Knee", "R_B_Knee", "L_F_Paw", "R_F_Paw",
    "L_B_Paw", "R_B_Paw"
]

# YOLO 标注格式中的类别 ID（假设为 0）
CLASS_ID = '0'

# 颜色配置
BOX_COLOR = (0, 255, 0)       # 绿色边框
POINT_COLOR = (0, 0, 255)     # 红色关键点
TEXT_COLOR = (255, 0, 0)      # 蓝色文本
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
THICKNESS = 2

def yolo_to_bbox(x_center, y_center, width, height, img_width, img_height):
    """
    将 YOLO 格式的坐标转换为边界框的左上角和右下角坐标。
    """
    x_center *= img_width
    y_center *= img_height
    width *= img_width
    height *= img_height

    x1 = int(x_center - width / 2)
    y1 = int(y_center - height / 2)
    x2 = int(x_center + width / 2)
    y2 = int(y_center + height / 2)

    return x1, y1, x2, y2

def draw_annotations(image, annotation_file):
    """
    在图像上绘制标注信息。
    """
    with open(annotation_file, 'r') as file:
        lines = file.readlines()

    img_height, img_width = image.shape[:2]

    for line in lines:
        parts = line.strip().split()
        if not parts or parts[0] != CLASS_ID:
            continue  # 只处理指定类别 ID 的标注

        # 解析边界框
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])

        x1, y1, x2, y2 = yolo_to_bbox(x_center, y_center, width, height, img_width, img_height)

        # 绘制边界框
        cv2.rectangle(image, (x1, y1), (x2, y2), BOX_COLOR, 2)

        # 解析并绘制关键点
        # 每个关键点有三个值：x, y, visibility
        # YOLO 格式中的坐标是相对于图像宽高的比例
        keypoints = parts[5:]
        num_keypoints = 20
        for i in range(num_keypoints):
            idx = i * 3
            if idx + 2 >= len(keypoints):
                break  # 防止索引超出

            x = float(keypoints[idx])
            y = float(keypoints[idx + 1])
            visibility = keypoints[idx + 2]

            if visibility != '0':
                px = int(x * img_width)
                py = int(y * img_height)
                cv2.circle(image, (px, py), 3, POINT_COLOR, -1)
                cv2.putText(image, KEYPOINT_NAMES[i], (px + 5, py - 5), FONT, FONT_SCALE, TEXT_COLOR, 1, cv2.LINE_AA)

    return image

def main():
    # 遍历图像目录中的所有图像文件
    for filename in os.listdir(IMAGE_DIR):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
            continue  # 跳过非图像文件

        image_path = os.path.join(IMAGE_DIR, filename)
        annotation_filename = os.path.splitext(filename)[0] + '.txt'
        annotation_path = os.path.join(ANNOTATION_DIR, annotation_filename)

        if not os.path.exists(annotation_path):
            print(f"标注文件不存在: {annotation_path}")
            continue

        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            continue

        # 绘制标注
        annotated_image = draw_annotations(image, annotation_path)

        # 保存结果
        output_path = os.path.join(OUTPUT_DIR, filename)
        cv2.imwrite(output_path, annotated_image)
        print(f"已保存标注图像: {output_path}")

if __name__ == "__main__":
    main()
