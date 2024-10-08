import glob
import tqdm
import torch
import random
import numpy as np
import pandas as pd
from PIL import Image
from pathlib import Path
from torchvision.transforms import v2

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
coco_data_path = project_base_path / 'data' / 'external' / 'COCO'
ns6_wiki_paths = (project_base_path / 'data' / 'processed' / 'wikimedia_commons').glob('ns6_*.parquet')

class HandlabelledDataset(torch.utils.data.Dataset):
    def __init__(self, transforms, train = True):
        df = pd.read_csv(project_base_path / 'data' / 'processed' / 'rotation_handmade' / 'rotations.csv')
        df = df.loc[200:] if train else df.loc[:200]
        df = df.reset_index()

        self.__impaths = df.loc[:, 'image_path']
        self.__targets = df.loc[:, 'rotation']
        self.__transforms = transforms
    def __len__(self):
        return len(self.__impaths)

    def __getitem__(self, idx):
        im = self.__transforms(Image.open(project_base_path / self.__impaths[idx])).float()
        t = self.__targets[idx]
        return im, t

class COCODataset(torch.utils.data.Dataset):
    def __init__(self, transforms, train = True):
        self.__transforms = transforms
        self.__foldername = coco_data_path / ('train2014' if train else 'val2014')
        self.__imnames = glob.glob(str(self.__foldername) + '/*.jpg')
        
    def __len__(self):
        return len(self.__imnames)

    def __getitem__(self, idx):
        t = random.choice([0, 1, 2, 3]) # randomly rotate the image
        im = self.__transforms(Image.open(self.__imnames[idx])).float()
        
        return v2.functional.rotate(im, t * 90), t

class WikimediaDataset(torch.utils.data.Dataset):
    def __init__(self, transforms, i):
        assert type(i) == int and (0 <= i < 8)
        df = pd.read_parquet(project_base_path / f'data/processed/wikimedia_commons/ns6_{i}.parquet', columns = ['image_path'])
        download_errors = ('Not Downloaded - Download Error', 'Not Downloaded - Transformation Error', 'Not Downloaded - Saving Error')
        bool_mask = ~df.loc[:, 'image_path'].isin(download_errors)

        self.__impaths = (
            df
            .loc[bool_mask, 'image_path']
            .drop_duplicates()
            .replace(to_replace = 'nan', value = np.nan)
            .dropna()
            .reset_index(drop = True)
        )
        self.__transforms = transforms
    def __len__(self):
        return len(self.__impaths)

    def __getitem__(self, idx):
        impath = self.__impaths[idx]
        im = self.__transforms(Image.open(project_base_path / self.__impaths[idx])).float()
        
        return im, impath

def train_eval(network, epochs, lr, momentum, dl_train, dl_test, verbose = True):
    loss = torch.nn.CrossEntropyLoss(weight = torch.tensor([0.1, 3, 12, 6]))
    optimizer = torch.optim.SGD(params = network.parameters(), 
                                lr = lr, 
                                momentum = momentum) 
    device = torch.device('cpu')
    network = network.to(device)

    for epoch in tqdm.tqdm(range(epochs), desc = 'Main Loop'):
        # Training loop
        network.train()
        for x, t in (tqdm.tqdm(dl_train, desc = 'Train') if verbose else dl_train):
          x = x.to(device); t = t.to(device)
          optimizer.zero_grad()
          z = network(x)
          J = loss(z, t)
          J.backward()
          optimizer.step() 

        # Testing loop
        network.eval()
        with torch.no_grad():
          correct, total, accumulated_loss = 0, 0, 0

          for x, t in (tqdm.tqdm(dl_train, desc = 'Test') if verbose else dl_test):
            x = x.to(device); t = t.to(device)
            z = network(x)
            J = loss(z, t)
        
            correct += torch.sum(
                torch.argmax(z, dim=1) == t
            ).item()
            accumulated_loss += J.item()
            total += t.shape[0]

        # Calculate and print accuracies and losses for current epoch
        print('Epoch:', epoch + 1)
        print('Loss:', accumulated_loss / total)
        print('Accuracy', correct / total, '\n')