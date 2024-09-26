import torch
from pathlib import Path
from matplotlib import pyplot as plt
from torchvision.transforms import v2
from sklearn.metrics import confusion_matrix
from rotnet50_helpers import HandlabelledDataset
from sklearn.metrics import ConfusionMatrixDisplay, recall_score, precision_score

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
output_path = project_base_path / 'reports' / 'figures'

network = torch.load(project_base_path / 'models' / 'rotnet50_retrained.pth')
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
ConfusionMatrixDisplay(confusion_matrix = conf_matrix, display_labels = ['0º', '90º', '180º', '270º']).plot()
plt.title('Confusion Matrix for the Rotation \nClassification Exercise')
plt.savefig(output_path / 'rotation_classifier_confusion_matrix.pdf', bbox_inches = 'tight')
plt.savefig(output_path / 'rotation_classifier_confusion_matrix.png', bbox_inches = 'tight')
plt.show()

ps_binarized = [0 if x == 0 else 1 for x in torch.cat(ps).tolist()]
ts_binarized = [0 if x == 0 else 1 for x in torch.cat(ts).tolist()]
print('Recall:', recall_score(ts_binarized, ps_binarized))
print('Precision:', precision_score(ts_binarized, ps_binarized))