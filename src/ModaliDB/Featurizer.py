'''
Class: Featurizer
=================

Description:
------------
	
	Class for featurizing frames

##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
class Featurizer(object):
	"""
		Example Usage:
		--------------
		
		# Create a trivial featurizer:
		@Featurizer('trivial_features'):
		def trivial_featurize(frame):
			return np.array([1, 2, 3])
	"""

	def __init__(self, feature_name):
		"""
			feature_name: feature name (will be saved under this)
		"""
		self.feature_name = feature_name
		self.feature_function = feature_function



	def load(self, path):
		"""
			describes how to load feature files 
		"""
		raise NotImplementedError


	def save(self, path):
		"""
			describes how to save feature files 
		"""
		raise NotImplementedError











