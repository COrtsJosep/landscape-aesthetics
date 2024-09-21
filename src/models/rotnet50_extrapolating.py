import os
import tqdm
import torch
import pandas as pd
from pathlib import Path
from torchvision.transforms import v2
from rotnet50_helpers import WikimediaDataset

file_location_path = Path(__file__)
project_base_path = file_location_path.parent.parent.parent
out_folder_path = project_base_path / 'data' / 'processed' / 'rotation_predicted'
    
network = torch.load(project_base_path / 'models' / 'rotnet50_retrained.pth')
network.eval()

transforms = v2.Compose([
    v2.PILToTensor(),
    v2.Resize(size = (224, 224)),
    v2.ToDtype(torch.float32, scale = True),
    v2.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225))
])

for i in range(1, 8):
    num_workers = min(4, os.cpu_count()) 
    ds = WikimediaDataset(transforms = transforms, i = i)
    dl = torch.utils.data.DataLoader(ds, 64, shuffle = False, num_workers = num_workers)
    
    predictions = []
    impaths = []
    
    with torch.no_grad():
        for im, impath in tqdm.tqdm(dl, desc = str(i)):
            predictions += torch.argmax(network(im), dim = 1).tolist()
            impaths += list(impath)
        
    df = pd.DataFrame(data = {'image_path': impaths, 'rotation': predictions})
    df.to_parquet(out_folder_path / f'ns6_rotation_{i}.parquet', index = False)