#!/bin/bash
cd /home

# first: set up anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh # fetch installer
sha256sum Anaconda3-2024.02-1-Linux-x86_64.sh # verify integrity
bash Anaconda3-2024.02-1-Linux-x86_64.sh # run installer
conda --version # check
rm Anaconda3-2024.02-1-Linux-x86_64.sh # remove installer

# second: set up the environment
conda create -n geoproject python=3.12 # create environment geoproject
conda activate geoproject # turn it on babe
conda install -c conda-forge jupyterlab shapely geopy tqdm
conda install numpy pandas geopandas requests

# third: set up git
sudo apt update # update system package index
sudo apt install git # get git
git --version # check
# TODO: clone the repository