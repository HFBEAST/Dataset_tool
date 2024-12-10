import os
import json


def is_valid_points(points):
    """
    判断 points 是否包含两个有效的坐标点。
    有效的 points 应该是一个包含两个列表的列表，每个内部列表包含两个数字。
    """
    if not isinstance(points, list):
        return False
    if len(points) != 2:
        return False
    for point in points:
        if not isinstance(point, list) or len(point) != 2:
            return False
        if not all(isinstance(coord, (int, float)) for coord in point):
            return False
    return True


def remove_invalid_shapes(json_data):
    """
    删除 shapes 列表中 points 仅包含一个空列表的标注对象。
    """
    if "shapes" not in json_data:
        return json_data, 0  # 如果没有 shapes 键，直接返回原数据

    original_shape_count = len(json_data["shapes"])
    # 保留 points 有两个有效坐标点的 shape 对象
    json_data["shapes"] = [
        shape for shape in json_data["shapes"]
        if is_valid_points(shape.get("points", []))
    ]
    removed_count = original_shape_count - len(json_data["shapes"])
    return json_data, removed_count


def process_json_files(directory, overwrite=True, backup=True):
    """
    处理指定目录下的所有 JSON 文件，删除 points 仅包含一个空列表的 shape 对象。

    参数:
    - directory: 要处理的目录路径。
    - overwrite: 是否覆盖原文件。True 表示覆盖，False 表示另存为新文件。
    - backup: 是否在覆盖前备份原文件。仅在 overwrite=True 时有效。
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"跳过无法解析的 JSON 文件: {file_path}. 错误: {e}")
                continue
            except Exception as e:
                print(f"跳过无法读取的文件: {file_path}. 错误: {e}")
                continue

            modified_data, removed = remove_invalid_shapes(data)

            if removed > 0:
                if backup and overwrite:
                    backup_path = file_path + ".backup"
                    try:
                        os.rename(file_path, backup_path)
                        print(f"备份原文件: {backup_path}")
                    except Exception as e:
                        print(f"无法备份文件: {file_path}. 错误: {e}")
                        continue

                if overwrite:
                    save_path = file_path
                else:
                    base, ext = os.path.splitext(file_path)
                    save_path = f"{base}_modified{ext}"

                try:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        json.dump(modified_data, f, ensure_ascii=False, indent=2)
                    print(f"处理文件: {file_path}. 删除了 {removed} 个无效 points 的 shape 对象.")
                except Exception as e:
                    print(f"无法保存修改后的文件: {save_path}. 错误: {e}")
            else:
                print(f"文件未修改 (无无效 points 的 shape 对象): {file_path}")


if __name__ == "__main__":
    # 设置要处理的目录路径
    target_directory = r"E:\SUBPJ\GIO\aiba\dataset\horse_sum_2500"  # 请将此处替换为您的 JSON 文件所在目录路径

    # 调用函数处理 JSON 文件
    process_json_files(
        directory=target_directory,
        overwrite=True,  # 设置为 True 以覆盖原文件，设置为 False 以另存为新文件
        backup=True  # 仅在 overwrite=True 时有效，是否备份原文件
    )
