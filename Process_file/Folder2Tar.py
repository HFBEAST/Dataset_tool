import tarfile
import os

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w") as tar:
        # 递归添加目录到tar文件
        tar.add(source_dir, arcname=os.path.basename(source_dir))

# 调用函数
make_tarfile('horses.tar', r'H:\DATASET\COCO_horse\horses')
