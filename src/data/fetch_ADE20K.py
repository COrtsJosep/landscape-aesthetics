import os
import requests
import zipfile


current_directory = os.getcwd()
download_dir = os.path.join(current_directory, '../../data/external')  


os.makedirs(download_dir, exist_ok=True)


def download_ade20k(download_dir):
    url = 'http://data.csail.mit.edu/places/ADEchallenge/ADEChallengeData2016.zip'
    zip_path = os.path.join(download_dir, 'ADEChallengeData2016.zip')


    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded ADE20K dataset to {zip_path}")


    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(download_dir)
    print(f"Extracted ADE20K dataset to {download_dir}")


    os.remove(zip_path)
    print(f"Removed the zip file {zip_path}")


download_ade20k(download_dir)
