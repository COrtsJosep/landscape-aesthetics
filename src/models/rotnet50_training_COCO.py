import torch
import torchvision
from pathlib import Path
from torchvision.transforms import v2
from rotnet50_helpers import COCODataset, train_eval

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.CenterCrop(size = (600, 600)),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

ds_train = COCODataset(transforms = transforms, train = True)
dl_train = torch.utils.data.DataLoader(ds_train, 32, shuffle = True)

ds_test = COCODataset(transforms = transforms, train = False)
dl_test = torch.utils.data.DataLoader(ds_test, 64, shuffle = True)

network = torchvision.models.resnet50(weights = 'DEFAULT')
network.fc = torch.nn.Linear(in_features = 512 * 4, out_features = 4)

### Training
train_eval(network = network, 
           epochs = 3, 
           lr = 0.001, 
           momentum = 0.9, 
           dl_train = dl_train, dl_test = dl_test,
           verbose = True
)
torch.save(network, project_base_path / 'models' / 'rotnet50_COCO.pth')