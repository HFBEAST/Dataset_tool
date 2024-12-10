import os
import sys

# 配置参数
folder_path = r"E:\DATASET\sum"  # 替换为您的文件夹路径，例如 "C:/Users/用户名/Pictures"
step = 20  # 每隔多少张保留一张

# 支持的图片扩展名
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

def is_image_file(filename):
    return os.path.splitext(filename.lower())[1] in image_extensions

def main():
    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹路径 '{folder_path}' 不存在或不是一个文件夹。")
        sys.exit(1)

    # 获取所有图片文件，按名称排序
    files = sorted([f for f in os.listdir(folder_path) if is_image_file(f)])

    print(f"总共有 {len(files)} 张图片。")

    for idx, image_file in enumerate(files):
        # 保留每隔 step 的图片，从第一个开始
        if idx % step != 0:
            base_name = os.path.splitext(image_file)[0]
            json_file = base_name + '.json'

            image_path = os.path.join(folder_path, image_file)
            json_path = os.path.join(folder_path, json_file)

            # 删除图片
            try:
                os.remove(image_path)
                print(f"已删除图片: {image_file}")
            except Exception as e:
                print(f"删除图片 {image_file} 时出错: {e}")

            # 删除对应的 JSON 文件
            if os.path.exists(json_path):
                try:
                    os.remove(json_path)
                    print(f"已删除 JSON 文件: {json_file}")
                except Exception as e:
                    print(f"删除 JSON 文件 {json_file} 时出错: {e}")
            else:
                print(f"警告: 对应的 JSON 文件 '{json_file}' 不存在。")
        else:
            print(f"保留图片: {image_file}")

    print("操作完成。")

if __name__ == "__main__":
    main()
