#!/bin/bash
cd /home/ubuntu

# first: set up anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh # fetch installer
sha256sum Anaconda3-2024.02-1-Linux-x86_64.sh # verify integrity
bash Anaconda3-2024.02-1-Linux-x86_64.sh # run installer
conda --version # check
rm Anaconda3-2024.02-1-Linux-x86_64.sh # remove installer

# second: set up the environment
conda create -n geoproject python=3.12 # create environment geoproject
conda activate geoproject # turn it on babe
conda install numpy pandas geopandas requests cairosvg inflection
conda install -c conda-forge jupyterlab shapely geopy tqdm fastparquet basemap

# TODO: clone the repository
cd /home/ubuntu/.ssh
ssh-keygen -t rsa -b 4096 -C "josep.cunqueroorts@uzh.ch" -f "COrtsJosep"
cat COrtsJosep.pub # to be able to add it to GitHub
ssh -i COrtsJosep -T git@github.com # check
touch config
nano config
## Then add the following 5 lines without the first #. Paste them, close with "CTRL + x", save, same name
## GitHub - COrtsJosep
#Host COrtsJosep
#        HostName github.com
#        User git
#        IdentityFile ~/.ssh/COrtsJosep

cd /home/ubuntu
git clone git@github.com:COrtsJosep/landscape-aesthetics.git --config core.sshCommand="ssh -i ~/.ssh/COrtsJosep"
cd /home/ubuntu/landscape-aesthetics
git config user.email "josep.cunqueroorts@uzh.ch"
git config user.name "Josep"
