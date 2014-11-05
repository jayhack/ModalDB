'''
Class: DataObject
=================

Description:
------------
	
	Common ancestor of objects that store data both in-memory and 
	on disk. This is useful for applications in which there are components 
	that are both very large and very small (i.e. text and associated images)

	Key properties:
		- abstracts away details of what items are stored where
		- loads items on disk lazily

	Terminology:
		- item: key, value pair
		- mongo_dict: representation that appears in mongodb, containing 
					fast-access items 
		- root: path to directory containing slow-access items



Example Usage:
--------------
	
	data_object = DataObject(schema, mongo_dict, root)
	data_object.set_schema(schema)

##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
import os
from collections import defaultdict

class DataObject(object):
	"""
		Example Usage:
		--------------

			data_object = DataObject(root, schema, contents)
			data_object.set_schema(schema)

	"""

	def __init__(self, db, mongo_dict, root):
		"""
			schema: dict describing layout and modes of interaction with contents
			mongo_dict: dict containing data from mongodb (for fast read/write in memory)
			root: root directory containing data on disk (for slower read/write of larger sizes)
		"""
		self.db = db
		self.schema = db.schema[type(self)]
		self.mongo_dict = mongo_dict
		self.disk_dict = {k:None for k in self.schema.keys() if not self.schema[k]['in_memory']}
		self.root = root


	################################################################################
	####################[ Properties	]###########################################
	################################################################################

	@property
	def schema(self):
	    return self._schema
	@schema.setter
	def schema(self, value):
	    self._schema = value


	@property
	def root(self):
	    return self._root
	@root.setter
	def root(self, value):
	    self._root = value


	def keys(self):
	    return self.schema.keys()


	def __contains__(self, name):
		return name in self.keys



	################################################################################
	####################[ Accessing Contents	]###################################
	################################################################################

	def get_path(self, key):
		"""
			returns path to file storing item named by key 
		"""
		return os.path.join(self.root, self.schema[key]['filename'])


	def load_disk_item(self, key):
		"""
			Loads item named by key
		"""
		self.disk_dict[key] = self.schema[key]['load_func'](self.get_path(key))


	def save_disk_item(self, key):
		"""
			Saves item named by key
		"""
		self.schema[name]['save_func'](self.get_path(key))


	def __getitem__(self, key):

		#=====[ Case: nonexistant item	]=====
		if not key in self.schema:
			raise AttributeError('No such item: %s' % key)

		#=====[ Case: in-memory item ]=====
		elif self.schema[key]['in_memory']:
			return self.mongo_dict[key]

		#=====[ Case: on-disk item	]=====
		else:
			if self.disk_dict[key] is None:
				self.load_disk_item(key)
			return self.disk_dict[key]


	def __setitem__(self, key, value):
		
		#=====[ Case: nonexistant item	]=====
		if not key in self.schema:
			raise AttributeError('No such item: %s' % key)

		#=====[ Case: in-memory item	]=====
		elif self.schema[key]['in_memory']:
			self.mongo_dict[key] = value

		#=====[ Case: on-disk item	]=====
		else:
			self.disk_dict[key] = value
			self.save_disk_item(key)


	def item_exists(self, key):
		"""
			returns true if the item named by key exists,
			wether thats in mongodb or on disk 
		"""
		#=====[ Case: nonexistant item	]=====
		if not key in self.schema:
			raise AttributeError('No such item: %s' % key)

		#=====[ Case: in-memory item	]=====
		elif self.schema[key]['in_memory']:
			return key in self.mongo_dict

		#=====[ Case: on-disk item	]=====
		else:
			return os.path.exists(self.get_path(key))



