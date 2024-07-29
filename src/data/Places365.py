from torchvision.datasets import Places365
from torchvision import transforms

# Define image transformation operations.
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

# Load training set
train_dataset = Places365(
    root='../../data/external/Places365',
    split='train-standard',
    download=True,
    transform=transform
)

# Load validation set
val_dataset = Places365(
    root='../../data/external/Places365',
    split='val',
    download=True,
    transform=transform
)
