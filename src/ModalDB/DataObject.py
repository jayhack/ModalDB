'''
Class: DataObject
=================

Description:
------------
	
	Common ancestor of objects that store data both in-memory and 
	on disk. This is useful for applications in which there are components 
	that are both very large and very small (i.e. text, associated images)

	Key properties:
		- abstracts away details of what items are stored where
		- lazily loads items on disk

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
import dill as pickle
from copy import deepcopy

from ModalDicts import DiskDict, MemoryDict

class DataObject(object):
	"""
		Example Usage:
		--------------

			# Create DataObject (should be subclassed...)
			data_object = DataObject(mongo_doc, schema)

			# Access items on disk and in memory identically
			disk_item = data_object[disk_item_name] # loads from disk
			mem_item = data_object[mem_item_name] # grabs from MongoDB

		mongo_doc:
		----------
		contains:
			- _id: self identifier 
			- root: path to this object's directory
			- children: mapping from child type to children
			- items: metadata on contained items (exists, etc.)

	"""
	def __init__(self, mongo_doc, schema):
		"""
			Args:
			-----
			- mongo_doc: dict containing root, in-memory items
			- client: reference to ModalClient object
		"""
		self.id = mongo_doc['_id']
		self.root = mongo_doc['root']
		self.schema = schema
		self.items = {
						'disk':DiskDict(mongo_doc, self.schema),
						'memory':MemoryDict(mongo_doc, self.schema)
					}
		if 'children' in mongo_doc:
			self.children = mongo_doc['children']





	################################################################################
	####################[ ITEM ACCESS	]###########################################
	################################################################################

	def __contains__(self, key):
		return any([key in d for d in self.items.values()])


	def detect_keyerror(self, key):
		if not key in self:
			raise KeyError("No such item: %s" % key)


	def get_mode(self, key):
		return self.schema[key]['mode']


	def __getitem__(self, key):
		self.detect_keyerror(key)
		return self.items[self.get_mode(key)][key]


	def __setitem__(self, key, value):
		self.detect_keyerror(key)
		self.items[self.get_mode(key)][key] = value


	def __delitem__(self, key):
		self.detect_keyerror(key)
		del self.items[self.get_mode(key)][key]





	################################################################################
	####################[ ITEM METADATA ]###########################################
	################################################################################

	def update_item_metadata(self):
		"""
			updates self.mongo_doc to reflect current state
			(i.e. which items are present)
		"""
		for modal_dict in self.items.values():
			modal_dict.update_item_metadata()


	def present_items(self):
		"""
			returns set of names of items that are present
		"""
		return set.union(*[md.present_items() for md in self.items.values()])


	def absent_items(self):
		"""
			returns set of names of items that are in schema 
			yet not present 
		"""
		return set.union(*[md.absent_items() for md in self.items.values()])



	################################################################################
	####################[ CHILDREN	]###############################################
	################################################################################

	def child_types(self):
		return set(self.schema['contains'])

	def is_child_type(self, datatype):
		return datatype in self.child_types()

	def get_children_ids(self, datatype):
		assert self.is_child_type(datatype)
		return self.children[datatype.__name__]

	def get_child_dir(self, datatype):
		assert self.is_child_type(datatype)
		return os.path.join(self.root, datatype.__name__)

	def add_child(self, datatype, _id):
		assert self.is_child_type(datatype)
		self.get_children_ids(datatype).append(_id)

	def get_child(self, datatype, _id):
		assert self.is_child_type(datatype)
		raise NotImplementedError

	def iter_children(self):
		raise NotImplementedError







