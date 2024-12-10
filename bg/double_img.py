import cv2

# 读取原始图像
img = cv2.imread(r'H:\DATASET\bg\1_202401_052039.jpg')

# 使用双线性插值放大图像
height, width = img.shape[:2]
new_size = (width * 2, height * 2)
resized_img = cv2.resize(img, new_size, interpolation=cv2.INTER_LINEAR)

# 保存放大后的图像
cv2.imwrite('1resized_output.jpg', resized_img)
