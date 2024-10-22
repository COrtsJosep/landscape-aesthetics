import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import os

root_folder = '/home/ubuntu/landscape-aesthetics/'  
csv_file = 'selected_images_6_to_7.csv'  

df = pd.read_csv(csv_file)

rows = 25
cols = 20

# set up an A4 size plot
fig, axes = plt.subplots(rows, cols, figsize=(8.27, 11.69)) 
fig.subplots_adjust(hspace=0.5, wspace=0.5)

# keep the total number consistent
image_count = len(df)
max_images = rows * cols

# if image_count > max_images:
#     df = df.head(max_images)

for i, (img_path, score) in enumerate(zip(df['image_path'], df['predicted_score'])):
    row = i // cols
    col = i % cols

    # 加载图片
    img_full_path = os.path.join(root_folder, img_path)
    img = Image.open(img_full_path)

    # 调整图片大小
    img = img.resize((int(210 / cols * 10), int(297 / rows * 10)))  # 将图片调整到适合的大小

    # 在子图上显示图片
    axes[row, col].imshow(img)
    axes[row, col].axis('off')  # 不显示坐标轴

    # 在图片下方添加分数
    axes[row, col].set_title(f'{score:.2f}', fontsize=6)  # 设置字体大小

# save as a pdf file
plt.savefig('image_matrix_A4.pdf', bbox_inches='tight')
plt.show()
