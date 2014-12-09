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

@click.command()
@click.option('--feature_name', '-f', 	help='Name of the feature to gather')
@click.option('--outpaths', '-o',		help='Path to store resulting matrix', multiple=True)
@click.option('--subsample_rate', '-s', help="for a given rate, 1/rate of all frames' features will be gathered",
										default=1)
def gather_features(feature_names, outpaths, subsample_rate):

	#=====[ Step 1: Sanitize input	]=====
	if not len(feature_names) == len(outpaths):
		click.echo("Make sure there is exactly one outpath for each feature")

	#=====[ Step 1: Connect to db	]=====
	click.echo("---> Connecting to DB")
	db = ModalDB()

	#=====[ Step 2: Gather features	]=====
	click.echo("---> Gathering features")
	feature_lists = {k:[] for k in feature_names}
	for frame in db.iter_frames(verbose=True, subsample_rate=subsample_rate):
		if not any([f[k] is None for k in feature_names]):
			for k in feature_names:
				feature_lists[k].append(frame[k])

	#=====[ Step 3: Store gathered features	]=====
	click.echo("---> Storing gathered features")
	feature_matrices = {k:np.matrix(v) for k,v in feature_lists.items()}
	for name, path in zip(feature_names, outpaths):
		np.save(path, feature_names[name])




if __name__ == '__main__':
	gather_features()
	

