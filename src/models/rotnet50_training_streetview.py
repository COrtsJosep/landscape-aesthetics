import glob
import torch
import random
import torchvision
import numpy as np
from pathlib import Path
from torchvision.transforms import v2
from rotnet50_helpers import StreetviewDataset, train_eval

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
street_data_path = project_base_path / 'data' / 'external' / 'streetview'

prop = 0.8
train_idxs = np.random.choice(len(glob.glob(str(street_data_path) + '/*.png')), round(0.8*len(glob.glob(str(street_data_path) + '/*.png'))))
mask = np.isin(np.arange(len(glob.glob(str(street_data_path) + '/*.png'))), train_idxs)
test_idxs = np.arange(len(glob.glob(str(street_data_path) + '/*.png')))[mask]

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.CenterCrop(size = (600, 600)),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

ds_train = StreetviewDataset(transforms = transforms, idxs = train_idxs)
dl_train = torch.utils.data.DataLoader(ds_train, 8, shuffle = True)

ds_test = StreetviewDataset(transforms = transforms, idxs = train_idxs)
dl_test = torch.utils.data.DataLoader(ds_test, 16, shuffle = True)

network = torchvision.models.resnet50()
network.fc = torch.nn.Linear(in_features = 512 * 4, out_features = 4)

### Training
train_eval(network = network, 
           epochs = 1, 
           lr = 0.001, 
           momentum = 0.9, 
           dl_train = dl_train, dl_test = dl_test,
           verbose = True
)
torch.save(network, project_base_path / 'models' / 'rotnet50.pth')