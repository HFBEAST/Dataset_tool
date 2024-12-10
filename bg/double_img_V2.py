import cv2

# 读取原始图像
img = cv2.imread(r'H:\DATASET\bg\1_202401_052039.jpg')

# 获取原始图像尺寸
height, width = img.shape[:2]

# 定义新的尺寸（解析度翻倍）
new_size = (width * 2, height * 2)

# 使用双立方插值进行图像放大
resized_img = cv2.resize(img, new_size, interpolation=cv2.INTER_CUBIC)

# 保存放大后的图像
cv2.imwrite('resized_output.jpg', resized_img)
