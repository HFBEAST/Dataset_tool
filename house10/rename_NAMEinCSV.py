import pandas as pd


def rename_and_replace(input_file, columns_to_delete, custom_name):
    # 读取 CSV 文件
    df = pd.read_csv(input_file, header=None)

    # 定义替换对照关系
    replacement_dict = {
        'Nose': 'Nose',
        'Eye': 'R_Eye',
        'Nearknee': 'L_F_Knee',
        'Nearfrontfetlock': 'L_F_Paw',
        'Offknee': 'R_F_Knee',
        'Offfrontfetlock': 'R_F_Paw',
        'Shoulder': 'Throat',
        'Elbow': 'R_F_Elbow',
        'Wither': 'Withers',
        'Nearhindhock': 'L_B_Knee',
        'Nearhindfetlock': 'L_B_Paw',
        'Stifle': 'R_B_Elbow',
        'Offhindhock': 'R_B_Knee',
        'Offhindfetlock': 'R_B_Paw',
        'Ischium': 'TailBase'
    }

    # 获取第二行数据 (第二行的索引是1)
    second_row = df.iloc[1, :]

    # 替换第二行中的内容
    df.iloc[1, :] = second_row.replace(replacement_dict)

    # 删除指定的列
    df.drop(columns=columns_to_delete, axis=1, inplace=True)

    # 从第四行开始，将第一列的文件名修改为自定义格式
    for i in range(3, len(df)):
        new_context = f"{custom_name}_{i - 2}.png"
        df.iloc[i, 0] = new_context
        print('context has changed to ', new_context)

    # 保存修改后的 CSV 文件
    output_file = r'2333.csv'
    df.to_csv(output_file, index=False, header=False)


if __name__ == '__main__':
    input_file = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\Sample17\x_240.csv'
    custom_name = 'x'

    # 指定要删除的列索引（从 0 开始计数）
    columns_to_delete = [9, 10, 15, 16, 19, 20, 23, 24, 31, 32, 33, 34, 41, 42]  # 替换为你需要删除的列索引列表

    rename_and_replace(input_file, columns_to_delete, custom_name)
