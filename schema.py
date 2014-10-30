'''
Schema.py: define your database schema 
======================================

Description:
------------
	
	Describes how images are stored and accessed


##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
import cPickle
import numpy as np
import scipy as sp
from scipy.io import loadmat, savemat
from scipy.misc import imread, imsave

from ModaliDB import Video, Frame

Schema = {
	Frame: {

		'_id': 		{
						'in_memory':True,
					},

		'image':	{
						'in_memory':False,
						'filename':'image.jpg',
						'load_func':lambda p: imread(p),
						'save_func':None
					},

		'masks':	{
						'in_memory':False,
						'filename':'masks_and_scores.mat',
						'load_func':lambda p: loadmat(p, variable_names=['masks'])['masks'],
						'save_func':None
					},

		'scores':	{
						'in_memory':False,
						'filename':'masks_and_scores.mat',
						'load_func':lambda p: loadmat(p, variable_names=['scores'])['scores'],
						'save_func':None
					},

		'cnn_features':	{
						'in_memory':False,
						'filename':'features.npy',
						'load_func':lambda p: cPickle.load(p),
						'save_func':lambda x, p: cPickle.dump(x, open(p, 'w'))
					}
	},

	Video: {

		'_id': 	{
						'in_memory':True
		}
	}

}