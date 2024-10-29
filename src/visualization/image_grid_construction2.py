import pandas as pd
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

# path
root_folder = '/home/ubuntu/landscape-aesthetics/'
csv_file = '/home/ubuntu/landscape-aesthetics/data/processed/landscape_license_processed/Image_Grid/selected_images_6_to_7.csv'
output_pdf = '/home/ubuntu/landscape-aesthetics/src/visualization/image_grid_6_to_7_with_license_links.pdf'

# License info and correspondence 
license_mappings = {
    "pd": "PD",
    "cc0": "CC0",
    "cc-by": "CC BY",
    "cc-by-sa": "CC BY-SA"
}

def is_valid_license(license):
    """ Extract and simplify the name """
    if isinstance(license, str):  # ensure license is a string
        for valid_license, display_name in license_mappings.items():
            if license.lower().startswith(valid_license):
                return display_name  # return the name after correspondence
    return "Unknown"

# read csv file
df = pd.read_csv(csv_file)
rows = 25
cols = 20

# set distance 
x_spacing = 6  # horizontal distance
row_spacing = 3.5  # vertical distance 
margin = inch / 8  # page distance 1/8 inch

# calculate the size of each unit cell including the distance in between
cell_size = min((A4[0] - 2 * margin) / cols, (A4[1] - 2 * margin) / rows)  # calculate the size of the unit cell
img_size = cell_size - x_spacing  # size of the image needs to be slightly smaller than the size of te unit cell

# create a pdf
c = canvas.Canvas(output_pdf, pagesize=A4)

for i, (img_path, score, license, url) in enumerate(zip(df['image_path'], df['predicted_score'], df['license'], df['url'])):
    row = i // cols
    col = i % cols
    
    # calcuate the drawing position, add distance and add extrac vertical distance
    x = margin + col * cell_size + x_spacing / 2
    y = A4[1] - margin - (row + 1) * cell_size - row * row_spacing

    # adjust and resize the image to a square
    img_full_path = os.path.join(root_folder, img_path)
    img = Image.open(img_full_path)
    # img = img.resize((int(img_size), int(img_size)), Image.LANCZOS)
    img = img.resize((int(img_size * 2), int(img_size * 2)), Image.LANCZOS) 

    # save the temp image and draw it on the pdf file
    temp_img_path = f"/tmp/temp_image_{i}.jpg"
    img.save(temp_img_path, quality=95)
    c.drawImage(temp_img_path, x, y, width=img_size, height=img_size)
    os.remove(temp_img_path)  # delete the temp file

    # extract the license info
    simplified_license = is_valid_license(license)

    # show the score and license information 
    text_x = x + img_size / 2
    score_text_y = y - 4  
    license_text_y = score_text_y - 4  

    c.setFont("Helvetica", 4)
    c.drawCentredString(text_x, score_text_y, f"{score:.2f}")
    c.drawCentredString(text_x, license_text_y, f"{simplified_license}")

    # add hyperlink
    license_link_x1 = text_x - img_size / 4
    license_link_x2 = text_x + img_size / 4
    license_link_y1 = license_text_y - 3
    license_link_y2 = license_text_y + 3
    c.linkURL(url, (license_link_x1, license_link_y1, license_link_x2, license_link_y2), relative=1)

# save pdf file
c.save()

print('done')