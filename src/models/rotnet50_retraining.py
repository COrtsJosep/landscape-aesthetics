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
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent

network = torch.load(project_base_path / 'models' / 'rotnet50.pth')

class HandlabelledDataset(torch.utils.data.Dataset):
    def __init__(self, transforms, train = True):
        df = pd.read_csv(project_base_path / 'data/processed/rotation_handmade/rotations.csv')
        df = df.loc[150:] if train else df.loc[:150]
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

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

ds_train = HandlabelledDataset(transforms = transforms, train = True)
dl_train = torch.utils.data.DataLoader(ds_train, 5, shuffle = True)

ds_test = HandlabelledDataset(transforms = transforms, train = False)
dl_test = torch.utils.data.DataLoader(ds_test, 25, shuffle = True)

### Training
def train_eval(network, epochs, lr, momentum):
    loss = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(params = network.parameters(), 
                                lr = lr, 
                                momentum = momentum) 
    device = torch.device('cpu')
    network = network.to(device)

    for epoch in tqdm.tqdm(range(epochs), desc = 'Main Loop'):
        # Training loop
        network.train()
        for x, t in tqdm.tqdm(dl_train, desc = 'Train'):
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

          for x, t in tqdm.tqdm(dl_train, desc = 'Test'):
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

train_eval(network, 5, 0.001, 0.9)
torch.save(network, project_base_path / 'models' / 'rotnet50_retrained.pth')