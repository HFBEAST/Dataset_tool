import pandas as pd
import cv2
import os

# 读取 CSV 文件
csv_file_path = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\BrownHorseinShadow\a_309-1.csv'  # 替换为你的CSV文件路径
df = pd.read_csv(csv_file_path)

# 文件夹路径
image_folder_path = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\BrownHorseinShadow'  # 替换为图片文件所在的文件夹路径
output_folder_path = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\0___check'  # 替换为保存输出图片的路径


# 确保输出文件夹存在
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# 获取标注的 bodyparts 名称列表（跳过前三行：scorer, bodyparts, coords）
bodyparts = df.columns[1::2]  # 偶数列是 bodypart 名称 (x对应的列）

# 遍历每一行数据并在图片上绘制点和名称
for index, row in df.iterrows():
    image_name = row[0]  # 图片名称，例如 'a_1.png'
    # 获取标注点的坐标
    x_coords = row[1::2]  # 偶数索引列是x坐标
    y_coords = row[2::2]  # 奇数索引列是y坐标

    # 读取图片
    image_path = os.path.join(image_folder_path, image_name)
    image = cv2.imread(image_path)

    if image is None:
        print(f"Image {image_name} not found.")
        continue

    # 遍历坐标点并在图片上绘制
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        if pd.notnull(x) and pd.notnull(y):  # 确保坐标值有效
            center = (int(float(x)), int(float(y)))
            # 绘制圆点
            cv2.circle(image, center, radius=5, color=(0, 255, 0), thickness=-1)  # 绿色小圆点
            # 绘制点的名称
            point_name = bodyparts[i]  # 获取对应的 bodypart 名称
            cv2.putText(image, point_name, (center[0] + 5, center[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)  # 蓝色文本

    # 保存标注后的图片
    output_image_path = os.path.join(output_folder_path, image_name)
    cv2.imwrite(output_image_path, image)
    print(f"Annotated image saved: {output_image_path}")

print("所有图片都已标注并保存完成。")
