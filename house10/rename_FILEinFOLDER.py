import os
import re

def rename(input_path, custom_name):

    def process(file, index, custom_name):
        name, ext = os.path.splitext(file)
        new_name = f'{custom_name}_{index}{ext}'
        return new_name


    files = os.listdir(input_path)

    for index, file in enumerate(files, start=1):
        old_name = os.path.join(input_path, file)
        if os.path.isfile(old_name):
            new_name = process(file, index, custom_name)
            new_file_path = os.path.join(input_path, new_name)
            os.rename(old_name, new_file_path)
        else:
            print(f'Error: {old_name} is not a file')


if __name__ == '__main__':

    custom_name = 'g'
    input_path = r'E:\DATASET\horse10\Horses-Byron-2019-05-08\labeled-data\ChestnutHorseLight'

    rename(input_path, custom_name)