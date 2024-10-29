import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import os

root_folder = '/home/ubuntu/landscape-aesthetics/'  
csv_file = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_processed/Image_Grid/selected_images_6_to_7.csv'  

df = pd.read_csv(csv_file)
rows = 25
cols = 20

# set up an A4 size plot
fig, axes = plt.subplots(rows, cols, figsize=(8.27, 11.69)) 
# fig.subplots_adjust(hspace=0.5, wspace=0.5)
fig.subplots_adjust(hspace=0.2, wspace=0.1)

# keep the total number consistent
image_count = len(df)
max_images = rows * cols

# if image_count > max_images:
#     df = df.head(max_images)

for i, (img_path, score, license, url) in enumerate(zip(df['image_path'], df['predicted_score'], df['license'], df['url'])):
    row = i // cols
    col = i % cols

    # load image
    img_full_path = os.path.join(root_folder, img_path)
    img = Image.open(img_full_path)

    # resize image
    img = img.resize((int(210 / cols * 10), int(297 / rows * 10)))  

    # show the image on subplot
    axes[row, col].imshow(img)
    axes[row, col].axis('off')

    license_text = f"{score:.2f}\n({license})"
    axes[row, col].text(0.5, -0.1, license_text, fontsize=4, ha='center', transform=axes[row, col].transAxes, color="blue")

    # # add score under image
    # axes[row, col].text(0.5, -0.1, f'{score:.2f}', fontsize=6, ha='center', transform=axes[row, col].transAxes)
    # axes[row, col].set_title(f'{score:.2f}', fontsize=6)  

output_path = '/home/ubuntu/landscape-aesthetics/src/visualization/image_grid_6_to_7.pdf'
plt.savefig(output_path, bbox_inches='tight', dpi=300)

print("Done")