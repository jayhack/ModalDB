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

			data_object = DataObject(mongo_doc)
			data_object.set_schema(schema)

	"""

	def __init__(self, mongo_doc, nesting):
		"""
			mongo_doc: contains root, schema, etc.

			{
				'root':'/path/to/dataobject',
				'items':{
							...items...
						}
				'_id':'this_id'
				'children':{
								...
							},
				}

		"""
		self.mongo_doc = mongo_doc
		self.disk_dict = self.get_disk_dict()
		self.nesting = nesting



	################################################################################
	####################[ Properties	]###########################################
	################################################################################

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
	def children(self):
		"""
			dict containing all of this item's children 
		"""
		return self.mongo_doc['children']
	@children.setter
	def children(self, value):
		self.mongo_doc['children'] = value
	


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


	def item_exists(self, key):
		"""
			returns true if the item exists on disk 
		"""



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
	####################[ Accessing items	]#######################################
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




	################################################################################
	####################[ Children	]###############################################
	################################################################################

	def is_root_type(self):
		"""
			returns true if this datatype is a root type
			(has no parent)
		"""
		index = nesting.index(type(self))
		return index == 0


	def is_leaf_type(self):
		"""
			returns true if this datatype is a leaf type 
			(has no children)
		"""
		index = nesting.index(type(self))
		return index == len(nesting) - 1


	def get_child(self, _id):
		"""
			returns the named child, returning none if it doesn't exist
		"""
		if not _id in self.children:
			return None
		else:
			index = nesting.index(type(self))
			if index == len(nesting) - 1:
				raise Exception("This object has no children")
			child_type = nesting[index+1]
			return child_type(children[_id], nesting)


	def iter_children(self):
		"""
			iterates through all children as data objects 
		"""
		if is_leaf_type():
			return
			yield
		for k in self.children.keys():
			yield self.get_child(k)




	################################################################################
	####################[ Filesystem	]###########################################
	################################################################################

	def validate_filesystem(self):
		"""
			validates personal filesystem, then calls recursively on children 
		"""
		#=====[ Step 1: check root	]=====
		assert os.path.isdir(self.root)

		#=====[ Step 2: for each item, update...	]=====
		for k in self.disk_dict.keys():
			self.items[k]['exists'] = self.disk_item_exists(k)

		#=====[ Step 3: iterate on children	]=====
		for child in self.iter_children():
			child.validate_filesystem()



