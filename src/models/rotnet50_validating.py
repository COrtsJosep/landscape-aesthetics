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

network = torch.load(project_base_path / 'models' / 'rotnet50_retrained_COCO.pth')
network.eval()

class HandlabelledDataset(torch.utils.data.Dataset):
    def __init__(self, transforms):
        df = pd.read_csv(project_base_path / 'data/processed/rotation_handmade/rotations.csv').loc[:200]

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

ds = HandlabelledDataset(transforms = transforms)
dl = torch.utils.data.DataLoader(ds, 25, shuffle = True)

ps, ts = [], []
for im, t in dl:
    p = torch.argmax(network(im), dim = 1)
    ps.append(p); ts.append(t)

    print('Batch accuracy:', (p == t).float().mean().item())

print('Lowest acceptable accuracy:', (0 == torch.cat(ts)).float().mean().item())
print('Achieved accuracy:', (torch.cat(ps) == torch.cat(ts)).float().mean().item())

conf_matrix = confusion_matrix(y_true = torch.cat(ts), y_pred = torch.cat(ps))
ConfusionMatrixDisplay(confusion_matrix = conf_matrix, display_labels = [0, 1, 2, 3]).plot()
plt.show()