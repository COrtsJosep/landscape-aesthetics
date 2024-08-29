import torch
from pathlib import Path
from torchvision.transforms import v2
from rotnet50_helpers import HandlabelledDataset, train_eval

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent

network = torch.load(project_base_path / 'models' / 'rotnet50_pretrained_COCO.pth')

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

ds_train = HandlabelledDataset(transforms = transforms, train = True)
dl_train = torch.utils.data.DataLoader(ds_train, 25, shuffle = True)

ds_test = HandlabelledDataset(transforms = transforms, train = False)
dl_test = torch.utils.data.DataLoader(ds_test, 25, shuffle = True)

### Training
train_eval(network = network, 
           epochs = 5, 
           lr = 0.001, 
           momentum = 0.9, 
           dl_train = dl_train, dl_test = dl_test,
           verbose = False
)
torch.save(network, project_base_path / 'models' / 'rotnet50_retrained_COCO.pth')