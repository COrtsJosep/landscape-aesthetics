import glob
import tqdm
import torch
import random
import torchvision
import numpy as np
from PIL import Image
from pathlib import Path
from torchvision.transforms import v2

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
data_path = project_base_path / 'data' / 'external' / 'streetview'

prop = 0.8
train_idxs = np.random.choice(len(glob.glob(str(data_path) + '/*.png')), round(0.8*len(glob.glob(str(data_path) + '/*.png'))))
mask = np.isin(np.arange(len(glob.glob(str(data_path) + '/*.png'))), train_idxs)
test_idxs = np.arange(len(glob.glob(str(data_path) + '/*.png')))[mask]

class Dataset(torch.utils.data.Dataset):
    def __init__(self, transforms, idxs):
        self.__transforms = transforms
        self.__idxs = idxs

    def __len__(self):
        return len(self.__idxs)

    def __getitem__(self, idx):
        t = random.choice([0, 1, 2, 3]) # randomly rotate the image
        im = self.__transforms(Image.open(data_path / f'{self.__idxs[idx]}.png')).float()
        
        return v2.functional.rotate(im, t * 90), t

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.CenterCrop(size = (600, 600)),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

ds_train = Dataset(transforms = transforms, idxs = train_idxs)
dl_train = torch.utils.data.DataLoader(ds_train, 8, shuffle = True)

ds_test = Dataset(transforms = transforms, idxs = train_idxs)
dl_test = torch.utils.data.DataLoader(ds_test, 16, shuffle = True)

network = torchvision.models.resnet50()
network.fc = torch.nn.Linear(in_features = 512 * 4, out_features = 4)

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

train_eval(network, 1, 0.001, 0.9)
torch.save(network, project_base_path / 'models' / 'rotnet50.pth')