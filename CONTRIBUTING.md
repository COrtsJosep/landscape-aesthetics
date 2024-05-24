# Welcome to :evergreen_tree:_landscape-aesthetics_:evergreen_tree: contributing guide

Thank you for your interest in contributing! This document is meant to get you started with the repository, 
with setting up your connection to the ScienceCloud instance and the environment up there, and with 
writting code in a way that the structure of the repository is preserved. We are a lot of people contributing, after all,
so it is important that we coordinate well.

## Setting yourself up
First things first, if your invite to the repository expired, send a reminder to @COrtsJosep.
I strongly recommend that you take the [training lessons](https://www.zi.uzh.ch/en/teaching-and-research/science-it/computing/training.html)
on Linux (the instance is running on linux) and Science Cloud offered by the UZH IT admins. It will make 
many things easier.

### Connecting to the Science Cloud instance
Again, if your _public-key_ has not been added yet, send a reminder to @COrtsJosep. Once it has, you should be able to 
connect by running from your machine:
```
ssh-add PATH_TO_PRIVATE_KEY
ssh ubuntu@IP_ADDRESS
```
or alternatively:
```
ssh -i PATH_TO_PRIVATE_KEY ubuntu@IP_ADDRESS
```
When prompted with the question whether you want to connect, type "yes". Make sure you are connected to a UZH network,
or using the VPN. Otherwise the connection will not be established. If the connection is successful, your command
name should change to _ubuntu@scenicornotineurope_.

### What is already there
The Science Cloud instance is already equipped with Git, Python, and Anaconda. In particular, we have a conda environment
already set up, called _geoproject_. Working within an environment has many benefits (see for instance [this guide](https://www.freecodecamp.org/news/why-you-need-python-environments-and-how-to-manage-them-with-conda-85f155f4353c/)
on why), but for this project, mainly it makes it easier to keep control of which modules we use. This will be helpful
if we ever need to shut down the current instance and move to another one. Also, if we somehow,
through installing and deinstalling modules, we break the installation, we can just create another environment, instead of having
to completely uninstall Anaconda. Because of this, please always execute code inside of the _geoproject_ conda environment.

### Running jupyter-lab remotely
We do not have a visual interface to work with the instance. Writting code from the command line is a bit cumbersome,
so the best way to work is by tunneling with jupyter-lab. Effectively this means that you have the jupyter-lab interface
in the browser of your computer, but the code is running remotely, on the Science Cloud instance, and modifying the 
files there. To set it up, run on the instance:
```
conda activate geoproject
jupyter-lab --no-browser --port 8000
```
This should generate an URL similar to http://localhost:8000/lab?token=some_very_long_token.
Then run on your machine:
```
ssh-add PATH_TO_PRIVATE_KEY
ssh -NL 8000:localhost:8000 ubuntu@IP_ADDRESS
```
or alternatively:
```
ssh -i PATH_TO_PRIVATE_KEY -NL 8000:localhost:8000 ubuntu@IP_ADDRESS
```
 By now the connection should be established. Now you just need to copy the URL from above into your browser.

### Connecting your GitHub account
TODO

[managing multiple accounts](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-your-personal-account/managing-multiple-accounts)

[article from Medium](https://vivekumar08.medium.com/managing-multiple-github-accounts-on-a-single-machine-a-professional-guide-26eee841d411)

## Writing code
Great, now you are set up and ready to write code! Some things to consider:

### Structure of the project
The structure is heavily inspired from [Cookiecutter](https://cookiecutter-data-science.drivendata.org/v1/) and slightly from 
[The Hitchhiker’s Guide to Python,](https://docs.python-guide.org/writing/structure/). Please try to respect it. Data is stored in /data, divided on whether it is raw, processed, clean, or from external
sources. Code is in /src, divided depending on what the purpose is. Reports, references, jupyter notebooks, docs, etc., should be in their own folder too.

### Some guidelines and things to remember
- Always activate the conda environment before running any (Python) code (```conda activate geoproject```)
- With jupyter-lab you can write both notebooks and .py files.
- Try to add a message to your commits, mention the issues you are working on (```git commit -m "useful message, #11"```)
- When reading data files, creating folders, downloading stuff, always write the paths relatively, never on absolute terms. The module ```pathlib``` is very useful for that
- We aim for reproducibility. Never do anything by hand, everything must be code. Never modify and overwrite data
- When installing packages, always try ```conda install PACKAGE_NAME```, then ```conda install -c conda-forge PACKAGE_NAME```, and if nothing works, ```pip install PACKAGE_NAME```. Always in the environment
- If you install a new module, add it to the second section of the file /src/setup/machine_setup.sh
