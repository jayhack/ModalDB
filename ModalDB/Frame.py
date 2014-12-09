'''
Class: Frame
============

Description:
------------
	
	Interface to individual frames and their associated 
	metadata


##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
import os
import cPickle
from collections import defaultdict
import numpy as np
import scipy as sp
from scipy.misc import imread
from scipy.io import loadmat

from DataObject import DataObject


class Frame(DataObject):
	"""
		Example Usage:
		--------------

		# Access metadata
		image = frame['image']

		# Add metadata; saves to disk.
		frame['features'] = CaffeCNN.featurize(frame['image'])

		# Visualization
		plt.show(frame.visualize_mask(1))

	"""

	def __init__(self, mongo_doc, schema, client):
		super(Frame, self).__init__(mongo_doc, schema, client)
		



	################################################################################
	####################[ Masks 	]###############################################
	################################################################################

	def get_mask(self, mask_id):
		"""
			returns the mask_id-th mask
		"""
		return self['masks'][:,:,mask_id]


	def apply_mask(self, image, mask):
		"""
			multiplies the mask into the image 
		"""
		masked = self['image'].copy()
		masked[(mask == 0)] = 0
		return masked


	def top_n_masks(self, n):
		"""
			returns *list* of top n masks as:
				[(mask_ix, mask) ...]
		"""
		ordered_ixs = np.argsort(self['scores'][:,0])[::-1]
		return [(i, self.get_mask(i)) for i in ordered_ixs[:n]]


	def crop_object(self, mask, black=False):
		"""
			given a mask representing an object, returns the region 
			of the image that contains the object 
			setting black to true will crop objects with everything else 
			blacked out
		"""
		img = self['image'] if not black else self.apply_mask(self['image'], mask)
		nonzero_ixs = np.argwhere(mask)
		min_x, max_x = np.min(nonzero_ixs[:,0]), np.max(nonzero_ixs[:,0])
		min_y, max_y = np.min(nonzero_ixs[:,1]), np.max(nonzero_ixs[:,1])		
		return img[min_x:max_x, min_y:max_y, :]


	def top_n_cropped_object_proposals(self, n=10, black=False):
		"""
			returns the top n object proposals, cropped 
		"""
		return [(ix, self.crop_object(m, black=black)) for ix, m in self.top_n_masks(n)]





	################################################################################
	####################[ Visualzation 	]###########################################
	################################################################################

	def visualize_raw(self):
		"""
			returns the raw image as numpy array
		"""
		return self['image']


	def visualize_mask(self, mask_id):
		"""
			visualizes only the 'mask_id'th mask
		"""
		return self.apply_mask(self['image'], self.get_mask(mask_id))


	def __str__(self):
		return """Frame: %s""" % self._id



