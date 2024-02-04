from torch.utils.data import Dataset
from torchvision.transforms import v2
import pandas as pd
import os
import zipfile
from PIL import Image
import io
import torch

class ArtDataset(Dataset):
    """
    Dataset from https://github.com/cs-chan/ArtGAN/tree/master/WikiArt%20Dataset
    """
    def __init__(self, data_path, artist, num_images, split = "train", transform = None, randomize = True, seed = 42):
        super().__init__()
        self.artist = artist
        self.num_images = num_images
        self.split = split
        self.seed = seed
        self.df = pd.read_csv(os.path.join(data_path, f"wikiart_{split}.csv"))
        self.subset = self.subset()
        self.zip_path = os.path.join(data_path, "wikiart.zip")

        if transform:
            self.transform = transform
        else:
            self.transform = v2.Compose([
                v2.Resize(512),
                v2.ToImage(),
                v2.RandomCrop(512),
                v2.ToDtype(torch.float32)
            ])

    def __len__(self):
        return self.num_images

    def subset(self):
        filtered_df = self.df.query("artist == @self.artist")
        if self.split == "train":
            return filtered_df.sample(self.num_images, replace = False, random_state = self.seed, ignore_index = True)
        else:
            return filtered_df
            
    def __getitem__(self, idx):
        record = self.subset.loc[idx]
        img = None
        with zipfile.ZipFile(self.zip_path) as archive:
            f = archive.read(os.path.join("wikiart", record["path"]))
            file_bytes = io.BytesIO(f)
            with Image.open(file_bytes) as img:
                img = Image.open(file_bytes)
                img = self.transform(img)
        return img, record["genre_id"]

