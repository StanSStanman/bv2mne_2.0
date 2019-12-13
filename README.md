BV2MNE creates source models readable by MNE using cortical meshes generated using BrainVISA (MarsAtlas) and subcortical structures from Freesurfer.

Installation:
-------------

$ git clone git clone git@bitbucket.org:brainets/bv2mne.git (with public RSA/DSA key on bitbucket)  
$ cd bv2mne  
$ python setup.py develop --user  
$ python examples/create_forward_model.py  

Requirements:
-------------

Tested so far with mne-python version 0.18 (will be installed on setup)  
Should change version to MNE 0.19


