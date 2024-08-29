import torch
from pathlib import Path
from matplotlib import pyplot as plt
from torchvision.transforms import v2
from sklearn.metrics import confusion_matrix
from rotnet50_helpers import HandlabelledDataset
from sklearn.metrics import ConfusionMatrixDisplay

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent

network = torch.load(project_base_path / 'models' / 'rotnet50_retrained_COCO.pth')
network.eval()

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

ds = HandlabelledDataset(transforms = transforms, train = False)
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