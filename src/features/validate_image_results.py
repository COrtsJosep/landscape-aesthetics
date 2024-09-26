import tqdm
import torch
import pickle
import pandas as pd
from PIL import Image
from pathlib import Path
from torchvision.transforms import v2

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
ns6_wiki_paths = (project_base_path / 'data' / 'processed' / 'wikimedia_commons').glob('ns6_*.parquet')
unreadable_images_path = project_base_path / 'data' / 'processed' / 'wikimedia_commons' / 'unopenable_images.pkl'

df = pd.concat([
    pd
    .read_parquet(ns6_wiki_path, columns = ['image_path'])
    for ns6_wiki_path in ns6_wiki_paths
])

download_errors = ('Not Downloaded - Download Error', 'Not Downloaded - Transformation Error', 'Not Downloaded - Saving Error')
bool_mask = ~df.loc[:, 'image_path'].isin(download_errors)
impaths =  df.loc[bool_mask, 'image_path'].drop_duplicates()

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

unreadable_paths = []
for impath in tqdm.tqdm(impaths):
    try:
        transforms(Image.open(project_base_path / impath)).float()
    except Exception as e:
        unreadable_paths.append(impath)
        print(e, 'at image', impath)

print(len(unreadable_paths), 'images cannot be loaded.')

if unreadable_paths:
    with open(unreadable_images_path, 'wb') as f:
        pickle.dump(unreadable_paths, f)