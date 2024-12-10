import os
import json
import glob


def update_image_paths(directory):
    """
    遍历指定目录中的所有 JSON 文件，修改每个 JSON 文件中的 'imagePath'，
    将其图片名称更改为与 JSON 文件名相同，保留原始的图片扩展名。

    :param directory: 包含 JSON 文件的目标目录路径
    """
    # 获取所有 JSON 文件的路径列表
    json_files = glob.glob(os.path.join(directory, '*.json'))

    for json_file in json_files:
        try:
            # 获取 JSON 文件名（不含扩展名）
            json_filename = os.path.splitext(os.path.basename(json_file))[0]

            # 打开并读取 JSON 文件
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 获取 'imagePath' 的值
            image_path = data.get('imagePath')
            if not image_path:
                print(f"警告: 文件 {json_file} 中没有 'imagePath' 键。")
                continue

            # 提取图片的扩展名
            _, ext = os.path.splitext(image_path)
            if not ext:
                print(f"警告: 文件 {image_path} 没有扩展名，跳过。")
                continue

            # 构造新的图片名称（仅文件名，不含路径）
            new_image_name = f"{json_filename}{ext}"

            # 更新 JSON 数据中的 'imagePath'
            data['imagePath'] = new_image_name

            # 将更新后的数据写回 JSON 文件
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"已更新 {json_file} 中的 'imagePath' 为 '{new_image_name}'。")

        except json.JSONDecodeError:
            print(f"错误: 文件 {json_file} 不是有效的 JSON 格式。")
        except Exception as e:
            print(f"错误: 处理文件 {json_file} 时发生异常: {e}")


if __name__ == "__main__":
    # 替换为你的目标文件夹路径
    directory = r'E:\PJ\GIO\aiba\dataset\pose\1_net_1600_aiba_3200'  # 例如: r'C:\Users\你的用户名\Documents\json_files'
    update_image_paths(directory)
