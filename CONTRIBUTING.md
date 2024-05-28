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
Last step is to set up an ssh key so that you can pull and push code to and from the repository, from the Science Cloud instance. 
Since we are all writing code from the same machine, each of us should have their own ssh key. That way we can keep track of who does what.

First thing is creating your key. On the instance, run:
```
cd /home/ubuntu/.ssh
ssh-keygen -t rsa -b 4096 -C "YOUR_GITHUB_EMAIL" -f "YOUR_GITHUB_USERNAME"
cat YOUR_GITHUB_USERNAME.pub
```
After running ```ssh-keygen```, give a good password for the key. Now, the ```cat``` command should have printed out your publickey. 
Go to github.com > Settings > SHH and GPG keys > New SSH key. Give it a name and paste your publickey. To check if it works, 
run ```ssh -i YOUR_GITHUB_USERNAME -T git@github.com``` on the instance. 

Great, now your ssh key has been created and is linked to your GitHub account! The last step is to add some lines in the ssh 
configuration file. To be able to edit the file from the console, run ```nano config```. This will open up the editor. Now
please add the following 5 lines:
```
# GitHub - YOUR_GITHUB_USERNAME
Host YOUR_GITHUB_USERNAME
        HostName github.com
        User git
        IdentityFile ~/.ssh/YOUR_GITHUB_USERNAME
```
After pasting them, close the editor with ctrl + x, say yes to save, and press enter. That should be it!

Resources used:
- [Article from GitHub](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-your-personal-account/managing-multiple-accounts)
- [Article from Medium](https://vivekumar08.medium.com/managing-multiple-github-accounts-on-a-single-machine-a-professional-guide-26eee841d411)

## Writing code
Great, now you are set up and ready to write code! Some things to consider:

### First things first
Each time you want to contribute to the project, you have to connect to the remote repository. To do this, run the following commands:
```
eval `ssh-agent -s` # turns on ssh-agent
ssh-add -D # deactivates other people's keys
ssh-add /home/ubuntu/.ssh/YOUR_GITHUB_USERNAME # activates your key

cd /home/ubuntu/landscape-aesthetics # sets the current directory to the project folder
git config user.email "YOUR_GITHUB_EMAIL"  
git config user.name "YOUR_NAME"
git pull # always pull before you write any code

conda activate geopandas
```
Pro tip: you can run all of these 7 commands at once, separated with a semicolon (;).

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
- Try not to ```git add``` data files, especially images. First because the storage in GitHub is limited, and secondly because each image has a license and maybe some licences forbid re-publishing without attribution. 

### Screen
There is one last tool that can be useful if you want to run a program that will take long to finish. A problem with 
working with the remote Science Cloud instance is that if for a moment your connection is severed (like for instance
if your WiFi falls for a second, or your VPN disconnects), then your current session with the instance will hang forever
and you will have to close the connection and connect again. Also might happen if your computer goes into standby mode.
This is of course not good if you want to run a long program that might take hours or days to run.

The solution is using Screen. Screen is an already installed program that allows you to create new sessions, run processes there,
and push the sessions to the background, so that they keep on running even after you close your connection to the instance. You
can create as many sessions as you want (but try to close the ones you do not use anymore).
The basic usage is:
```
screen -ls # lists all active sessions
screen -S SCREEN_NAME # creates a session named SCREEN_NAME
```
After running that second line, you will land in the new screen session. It looks just like another console. Now you can run
whatever you want. For instance ```python very_long_process.py```. You might want to do something else in the meantime, so 
you want to switch back to the main session. To do that, press "ctrl-a + d". If you want to come back to the screen
running in the background, run ```screen -r SCREEN_NAME```. To kill a screen session, log into it and run ```exit```.

Those are the basics! You can do more things with it, but that was the most important. If you want to know more, here 
are some quick guides:
- [Linux Handbook](https://linuxhandbook.com/screen-command/)
- [Geeks for Geeks](https://www.geeksforgeeks.org/screen-command-in-linux-with-examples/)
- [Official Manual](https://www.gnu.org/software/screen/manual/screen.html)
