import tarfile
import os

def extract_tarfile(input_filename, target_dir):
    with tarfile.open(input_filename, "r") as tar:
        tar.extractall(path=target_dir)
    print(f'文件已解压到 {target_dir}')


target_directory = './'
input_tar_file = 'horses.tar'


extract_tarfile(input_tar_file, target_directory)
