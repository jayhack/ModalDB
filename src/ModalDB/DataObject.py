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
		- mongo_doc: representation that appears in mongodb, containing 
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

class DataObject(object):
	"""
		Example Usage:
		--------------

			data_object = DataObject(root, schema, contents)
			data_object.set_schema(schema)

	"""

	def __init__(self, mongo_doc):
		"""
			mongo_doc: contains root, schema, etc.

			{
				'root':'/path/to/dataobject',
				'items':{
							...items...
						}
				'_id':'this_id'
				}

		"""
		self.mongo_doc = mongo_doc
		self.disk_dict = self.get_disk_dict()


	################################################################################
	####################[ Properties	]###########################################
	################################################################################

	@property
	def items(self):
		"""
			dict mapping item name to it description and, possibly, contents 
		"""
		return self.mongo_doc['items']
	@items.setter
	def items(self, value):
		self.mongo_doc['items'] = value


	@property
	def root(self):
		"""
			path to this data object's root in filesystem
		"""
		return self.mongo_doc['root']
	@root.setter
	def root(self, value):
		self.mongo_doc['root'] = value


	@property
	def id(self):
		"""
			this data object's name
		"""
		return self.mongo_doc['_id']
	@id.setter
	def id(self, value):
		self.mongo_doc['_id'] = value
	

	def __contains__(self, name):
		"""
			allows for easy lookup of wether data object has this 
		"""
		return name in self.items


	################################################################################
	####################[ Disk items	]###########################################
	################################################################################

	def get_disk_dict(self, mongo_doc):
		"""
			given a mongo_doc, returns a dict mapping disk-items to None
		"""
		return {k:None for k,v in self.items if v['mode'] == 'disk'}


	def get_path(self, key):
		"""
			returns path to file storing item named by key 
		"""
		return os.path.join(self.root, self.items[key]['filename'])


	def load_disk_item(self, key):
		"""
			Loads item named by key
		"""
		self.disk_dict[key] = self.items[key]['load_func'](self.get_path(key))


	def save_disk_item(self, key):
		"""
			Saves item named by key
		"""
		assert not self.disk_dict[key] is None
		assert not self.items[key]['save_func'] is None
		self.items[key]['save_func'](self.disk_dict[key], self.get_path(key))




	################################################################################
	####################[ Accessing Contents	]###################################
	################################################################################

	def __getitem__(self, key):

		#=====[ Case: nonexistant item	]=====
		if not key in self:
			raise AttributeError('No such item: %s' % key)

		#=====[ Case: on-disk item	]=====
		elif self.items[key][mode] == 'disk':
			if self.disk_dict[key] is None:
				self.load_disk_item(key)
			return self.disk_dict[key]

		#=====[ Case: in-memory item ]=====
		elif self.items[key][mode] == 'memory':
			#####[ TODO: get items from memory	]#####
			raise NotImplementedError


	def __setitem__(self, key, value):
		
		#=====[ Case: nonexistant item	]=====
		if not key in self:
			raise AttributeError('No such item: %s' % key)

		#=====[ Case: in-memory item	]=====
		elif self.items[key][mode] == 'memory':
			#####[ TODO: set items in memory	]#####
			raise NotImplementedError

		#=====[ Case: on-disk item	]=====
		else:
			self.disk_dict[key] = value
			self.save_disk_item(key)


