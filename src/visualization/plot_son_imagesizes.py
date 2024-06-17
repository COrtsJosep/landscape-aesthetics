import pandas as pd
from PIL import Image
from pathlib import Path
from matplotlib import pyplot as plt

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
son_path = project_base_path / 'data' / 'external' / 'scenicornot'
output_path = project_base_path / 'reports'

def get_image_size(im_path):
    with Image.open(im_path) as im:
        return f'{im.size[0]}x{im.size[1]}' 

print('Calculating image sizes...')
df_im = (pd
         .read_csv(son_path / 'scenicornot.imagestatus.csv')
         #.sample(n = 1000)
         .query('image_status == "OK"')
         .assign(image_size = lambda df: df.loc[:, 'filename'].apply(lambda im_path: get_image_size(son_path / im_path)),
                 image_width = lambda df: df.loc[:, 'image_size'].apply(lambda size: int(size.split('x')[0])),
                 image_height = lambda df: df.loc[:, 'image_size'].apply(lambda size: int(size.split('x')[1]))
                )
)

print('Generating scatterplot...')
df_im.plot.scatter(x = 'image_width', 
                   y = 'image_height',
                   marker = 'x',
                   c = 'deepskyblue')

min_size = min(df_im.loc[:, 'image_width'].min(), df_im.loc[:, 'image_height'].min())
max_size = max(df_im.loc[:, 'image_width'].max(), df_im.loc[:, 'image_height'].max())
plt.plot([min_size, max_size], [min_size, max_size], c = 'k')

plt.xlabel('Image Width')
plt.ylabel('Image Height')
plt.title('Image Size, in Pixels')
plt.axis('square')

plt.savefig(output_path / 'figures' / 'son_image_sizes.pdf', 
            bbox_inches = 'tight')
plt.savefig(output_path / 'figures' / 'son_image_sizes.png', 
            bbox_inches = 'tight')
plt.show()

print('Generating first table...')
df_tex_size = (
    (df_im
    .groupby(by = 'image_size')
    .size()
    .sort_values(ascending = False) / df_im.shape[0])
)
df_tex_size.iloc[9] = df_tex_size.iloc[9:].sum()
df_tex_size.index = [name if i != 9 else 'Others' for i, name in enumerate(df_tex_size.index)]
df_tex_size = df_tex_size.head(10)

df_tex_size.to_latex(output_path / 'tables' / 'SoN_image_sizes.tex',
                caption = 'Proportion of images in the SoN database with each image size.',
                float_format = '%.3f',
                label = 'tab:SoNImageSizes')
display(df_tex_size)

print('\nGenerating second table...')
df_tex_short = (
    (df_im
    .assign(shortest_side = lambda df: df.loc[:, ['image_width', 'image_height']].min(axis = 1))
    .groupby(by = 'shortest_side')
    .size()
    .sort_values(ascending = False)) / df_im.shape[0]
)

df_tex_short.iloc[9] = df_tex_short.iloc[9:].sum()
df_tex_short.index = [name if i != 9 else 'Others' for i, name in enumerate(df_tex_short.index)]
df_tex_short = df_tex_short.head(10)

df_tex_short.to_latex(output_path / 'tables' / 'SoN_image_shortside.tex',
                caption = 'Proportion of images in the SoN database with each image shorter side size.',
                float_format = '%.3f',
                label = 'tab:SoNImageShortSize')
display(df_tex_short)

print('\nAll done!')