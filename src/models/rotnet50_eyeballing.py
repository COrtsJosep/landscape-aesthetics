import torch
from pathlib import Path
from matplotlib import pyplot as plt
from torchvision.transforms import v2
from rotnet50_helpers import WikimediaDataset

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent

network = torch.load(project_base_path / 'models' / 'rotnet50_retrained_COCO.pth')

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