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

			contains record of all items, including:
				- wether they are present or not (allows for fast search)
				- their mode of storage
				- NOT their load-funcs; this is handled in schema
				- if they are in-memory, contains their actual data



		Maybe try having multiple different dicts, like self.items[mode_name]['x']
		hmm... so mongo_doc doesn't get confused
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
	####################[ CHILDREN	]###############################################
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


	def get_child_type(self):
		"""
			returns child's type 
		"""
		self_index = self.nesting.index(type(self))
		if self_index == len(self.nesting) - 1:
			return None 
		else:
			return self.nesting[self_index + 1]


	def get_children_dir(self):
		"""
			returns path to directory where children reside 
			None if children don't exist
		"""
		child_type = self.get_child_type()
		if child_type:
			return os.path.join(self.root, child_type.__name__)
		else:
			return None


	def get_child(self, _id):
		"""
			returns the named child, returning none if it doesn't exist
		"""
		if not _id in self.children:
			return None
		else:
			return self.get_child_type()(chilrden[_id], self.nesting)


	def iter_children(self):
		"""
			iterates through all children as data objects 
		"""
		if 'children' in self.mongo_doc:
			for k in self.children:
				yield k
		else:
			return 
			yield


	def add_child(self, _id):
		"""
			creates a mongodb document representing a given data type 
		"""
		child_type = self.get_child_type()
		schema = self.client.schema.schema_dict[child_type]
		mongo_doc = {}

		#=====[ Step 1: make mongo_doc	]=====
		mongo_doc['root'] = os.path.join(self.root, child_type.__name__, _id)
		mongo_doc['_id'] = _id
		mongo_doc['items'] = deepcopy(schema)
		for item in mongo_doc['items'].values():
			if 'load_func' in item:
				item['load_func'] = pickle.dumps(item['load_func'])
			if 'save_func' in item:
				item['save_func'] = pickle.dumps(item['save_func'])
		for v in mongo_doc['items'].values():
			v['exists'] = False
		if not self.client.is_leaf_type(child_type):
			mongo_doc['children'] = []

		#=====[ Step 2: insert it into children	]=====
		self.children.append(mongo_doc)

		#=====[ Step 3: make object 	]=====
		child = child_type(mongo_doc, self.client)
		child.update()



	################################################################################
	####################[ Filesystem	]###########################################
	################################################################################

	def update(self):
		"""
			checks own filesystem in order to update
			mongo_doc
		"""
		#=====[ Step 1: check root	]=====
		if not os.path.isdir(self.root):
			os.mkdir(self.root)

		#=====[ Step 2: for each item, update...	]=====
		for k in self.disk_dict.keys():
			self.items[k]['exists'] = self.disk_item_exists(k)

		#=====[ Step 3: iterate on children	]=====
		child_type = self.get_child_type()
		if child_type:

			#=====[ Step 3.1: make directory for children	]=====
			if not os.path.isdir(self.get_children_dir()):
				os.mkdir(self.get_children_dir())

			#=====[ Step 3.2: add child if necessary	]=====
			for c_id in [x for x in os.listdir(self.get_children_dir()) if not x.startswith('.')]:
				if self.get_child(c_id) is None:
					self.add_child(c_id)

			#=====[ Step 3.3: call same for each child	]=====
			for child in self.iter_children():
				child.update()



