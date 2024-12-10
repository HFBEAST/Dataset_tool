import os
import json
import shutil
from pycocotools.coco import COCO

# 设置路径
annotations_dir = r'H:\DATASET\COCO2017\annotations'
images_dir = r'H:\DATASET\COCO2017\val'
output_dir = r'H:\DATASET\COCO_horse'
output_images_dir = os.path.join(output_dir, 'val')
output_annotations_dir = os.path.join(output_dir, 'annotations')
os.makedirs(output_images_dir, exist_ok=True)
os.makedirs(output_annotations_dir, exist_ok=True)

# 定义所需类别
desired_categories = ["horse"]

# 加载 COCO 标注
coco = COCO(os.path.join(annotations_dir, 'instances_val2017.json'))

# 获取类别 ID
category_ids = coco.getCatIds(catNms=desired_categories)
if not category_ids:
    raise ValueError("未找到指定的类别。请检查类别名称是否正确。")

# 获取包含所需类别的图像 ID
image_ids = set()
for cat_id in category_ids:
    img_ids = coco.getImgIds(catIds=cat_id)
    image_ids.update(img_ids)

# 获取图像信息
images = coco.loadImgs(list(image_ids))

# 创建新的 COCO 格式数据
new_coco = {
    "info": coco.dataset.get("info", {}),
    "licenses": coco.dataset.get("licenses", []),
    "images": images,
    "annotations": [],
    "categories": []
}

# 获取并添加类别信息
for cat_id in category_ids:
    cat = coco.loadCats(cat_id)[0]
    new_coco["categories"].append(cat)

# 获取相关标注
for img in images:
    ann_ids = coco.getAnnIds(imgIds=img['id'], catIds=category_ids, iscrowd=None)
    anns = coco.loadAnns(ann_ids)
    new_coco["annotations"].extend(anns)

# 保存新的标注文件
filtered_annotations_path = os.path.join(output_annotations_dir, 'val2017_horse.json')
with open(filtered_annotations_path, 'w') as f:
    json.dump(new_coco, f)

# 复制对应的图像到新的目录
for img in images:
    src = os.path.join(images_dir, img['file_name'])
    dst = os.path.join(output_images_dir, img['file_name'])
    if not os.path.exists(dst):
        shutil.copy(src, dst)

print(f"筛选完成！筛选后的数据集保存在 {output_dir}")
