'''
Script: gather_features.py
==========================

Description:
------------
	
	Allows one to gather features from all frames into a single 
	matrix for exporting, performing batch procedures, etc.

Usage: 
------

	python gather_features.py --feature_name [feature_name]

	e.g.

	python gather_features.py --feature_name caffe_cnn


##############
Jay Hack
Fall 2014
jhack@stanford.edu
##############
'''
import click
import numpy as np
from ModalDB import *
from schema import FrameSchema

@click.option('--feature_name', 	help='Name of the feature to gather')
@click.option('--outpath',			help='Path to store resulting matrix')
def gather_features(feature_name, outpath):

	#=====[ Step 1: connect to db	]=====
	@click.echo("---> Connecting to DB")
	db = ModalDB()

	#=====[ Step 2: gather features	]=====
	@click.echo("---> Gathering features")
	feature_vecs = []
	for frame in db.iter_frames(verbose=True):
		if not f['features'] is None:
			feature_vecs.append(frame[feature_name])

	#=====[ Step 3: store gathered features	]=====
	@click.echo("---> Storing gathered features")
	feature_vecs = np.matrix(feature_vecs)
	np.save(outpath, feature_vecs)







if __name__ == '__main__':

	sd = StorageDelegate()

	feature_vecs = []
	video_ids = []	
	frame_ids = []
	mask_ids = []

	for video in sd.iter_videos(verbose=True):
		for ix, f in enumerate(video.iter_frames(verbose=True)):
			if ix % 25 == 0:
				if not f.features is None:
					feature_vecs += f.features.values()
					video_ids += [video.name]*len(f.features.keys())
					frame_ids += [f.index]*len(f.features.keys())
					mask_ids += f.features.keys()

	print '=====[ ...SAVING... ]====='
	np.save('./data/feature_vecs', np.matrix(feature_vecs))
	np.save('./data/video_ids', np.array(video_ids))
	np.save('./data/frame_ids', np.array(frame_ids))
	np.save('./data/mask_ids', np.array(mask_ids))
	

