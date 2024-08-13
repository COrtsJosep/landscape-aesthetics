import glob
import tqdm
import torch
import random
import torchvision
import numpy as np
import pandas as pd
from PIL import Image
from pathlib import Path
from torchvision.transforms import v2
from matplotlib import pyplot as plt

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent

network = torch.load(project_base_path / 'models' / 'rotnet50.pth')

class WikimediaDataset(torch.utils.data.Dataset):
    def __init__(self, transforms):
        df = pd.read_parquet(project_base_path / 'data/processed/wikimedia_commons/ns6.parquet')
        download_errors = ('Not Downloaded - Download Error', 'Not Downloaded - Transformation Error', 'Not Downloaded - Saving Error')
        bool_mask = ~df.loc[:, 'image_path'].isin(download_errors)

        self.__impaths = df.loc[bool_mask, 'image_path'].drop_duplicates()
        self.__transforms = transforms
    def __len__(self):
        return len(self.__impaths)

    def __getitem__(self, idx):
        im = self.__transforms(Image.open(project_base_path / self.__impaths[idx])).float()
        
        return im

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

ds = WikimediaDataset(transforms = transforms)
dl = torch.utils.data.DataLoader(ds, 1, shuffle = True)

i = iter(dl)
for _ in range(10):
    im = next(i)
    prediction = torch.argmax(network(im), dim = 1).item()
    print(prediction)
    plt.imshow(im[0].permute(1, 2, 0))
    plt.show()