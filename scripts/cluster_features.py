'''
Script: cluster_features.py
===========================

Description:
------------
	
	Input: numpy matrix containing features 
	Output: cluster IDs for each featurized object


Args:
-----
	
	--inpath: path to file containing feature matrix 
	--outpath: path to location to save resulting cluster ids
	--n_clusters: number of clusters to use in KMeans 
	--normalize/--no-normalize: boolean flag for L2 normalizing before clustering

Usage:
------

	python cluster_features.py --inpath ./data/features.npy --outpath cluster_ids.npy ...
				--n_clusters 50 


##############
Jay Hack
Fall 2014
jhack@stanford.edu
##############
'''
import click
import os
import numpy as np
from sklearn import preprocessing, cluster
from ModaliDB import *

@click.command()
@click.option('--inpath', 					help='path to file containing feature vectors')
@click.option('--outpath', 					help='path to save cluster ids to')
@click.option('--n_clusters', 				help='number of centroids to cluster (default 50)', type=int, default=50, )
@click.option('--normalize/--no-normalize', help='Normalize features?', default=True)
def cluster_features(inpath, outpath, n_clusters, normalize):
	"""
		Clusters a feature matrix and outputs resulting 
		cluster ids
	"""
	#=====[ Step 1: Sanitize input	]=====
	if not os.path.exists(inpath):
		raise Exception("specified infile path nonexistent")

	#=====[ Step 2: Load/normalize input	]=====
	click.echo('---> Loading/normalizing input feature matrix')
	X = np.load(inpath)
	if normalize:
		X = preprocessing.normalize(X, norm='l2')

	#=====[ Step 3: Perform clustering ]=====
	click.echo('---> Performing KMeans clustering')
	cluster_ids = cluster.KMeans(n_clusters=n_clusters, verbose=1, n_jobs=1).fit_predict(X)

	#=====[ Step 4: Save output	]=====
	click.echo('---> Saving cluster IDs')
	np.save(outpath, cluster_ids)


if __name__ == '__main__':
	cluster_features()
