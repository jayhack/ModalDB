'''
Script: caffe_featurize.py
==========================

Description:
------------
	
	This script allows one to add features from a caffe-trained CNN to the filesystem
	and MongoDB back-end.

Usage: 
------

	python caffe_featurize.py


##############
Jay Hack
Fall 2014
jhack@stanford.edu
##############
'''
from ModalDB import *

if __name__ == '__main__':

	net = CaffeCNN()
	net.cnn # CaffeCNN lazily loads the cnn.

	db = ModalDB()
	for frame in db.iter_frames(verbose=True):
		if frame['features'] is None and not frame['masks'] is None:
			frame['features'] = net.featurize_frame(frame)




