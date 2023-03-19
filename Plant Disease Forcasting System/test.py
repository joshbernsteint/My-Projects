from PIL import Image
import os

annotated_images = []

for file in os.listdir(r'E:/Old Files/Mercury Project/annotated_images'):
    if file.endswith(".png"):
        annotated_images.append(file)

print(len(annotated_images))