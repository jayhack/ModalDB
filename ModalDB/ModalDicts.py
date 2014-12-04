'''
Module: ModalDicts
==================

Description:
------------
	
	Facilitates access to items in different modes of memory

Example Usage:
--------------
	
	disk_dict = DiskDict(mongo_doc)
	memory_dict = DiskDict(mongo_doc)
	...
	etc

##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
import os
from collections import defaultdict

class ModalDict(object):
	"""
		Base class for DiskDict, MemoryDict, DynamicDict
	"""

	def __init__(self, mongo_doc, datatype_schema):
		"""
			initializes self.keys, self.present, self.data
		"""
		assert not self.mode is None
		self.keys 		= set([k for k,v in datatype_schema.items() if not k == 'contains' and v['mode'] == self.mode])
		self.present 	= defaultdict(lambda: False, {k:True for k in mongo_doc['items'].keys()})
		self.data 		= defaultdict(lambda: None)


	def item_present(self, key):
		"""
			returns true if the named item present. Override.
		"""
		return self.present[key]
	

	@property
	def present_items(self):
		"""
			returns set of names of items that are present
		"""
		return set(filter(self.item_present, self.keys))


	@property
	def absent_items(self):
		"""
			returns set of items that are not present.
		"""
		return self.keys - self.present_items


	def __contains__(self, key):
		return key in self.keys


	def detect_keyerror(self, key):
		if not key in self:
			raise KeyError("No such item: %s" % key)


	def __getitem__(self, key):
		self.detect_keyerror(key)
		return self.get_item(key)


	def get_item(self, key):
		raise NotImplementedError


	def __setitem__(self, key, value):
		self.detect_keyerror(key)
		self.present[key] = True
		return self.set_item(key, value)


	def set_item(self, key, value):
		raise NotImplementedError


	def __delitem__(self, key):
		self.detect_keyerror(key)
		self.present[key] = False
		self.del_item(key)	


	def del_item(self, key):
		raise NotImplementedError







################################################################################
####################[ MemoryDict ]##############################################
################################################################################

class MemoryDict(ModalDict):
	"""
		Class: MemoryDict
		-----------------
		Facilitates access to items in memory (MongoDB)
	"""
	mode = 'memory'

	def __init__(self, mongo_doc, datatype_schema):
		super(MemoryDict, self).__init__(mongo_doc, datatype_schema)
		self.data.update({k:mongo_doc['items'][k] for k in self.present_items})


	def get_item(self, key):
		self.detect_keyerror(key)
		return self.data[key]


	def set_item(self, key, value):
		self.data[key] = value


	def del_item(self, key):
		self.data[key] = None





################################################################################
####################[ DiskDict ]################################################
################################################################################

class DiskDict(ModalDict):
	"""
		Class: DiskDict
		---------------
		Facilitates access to items on disk
	"""
	mode = 'disk'

	def __init__(self, mongo_doc, datatype_schema):
		super(DiskDict, self).__init__(mongo_doc, datatype_schema)

		root = mongo_doc['root']
		items = datatype_schema

		self.load_funcs = {k:items[k]['load_func'] for k in self.keys}
		self.save_funcs = {k:items[k]['save_func'] for k in self.keys}
		self.paths 		= {k:os.path.join(root, items[k]['filename']) for k in self.keys}
		self.data 		= {k:None for k in self.keys}

		self.check_paths_exist()


	def check_paths_exist(self):
		"""
			makes sure that all items listed actually exist
		"""
		for k in self.present_items:
			if not os.path.exists(self.paths[k]):
				raise Exception("Item %s not on disk (should be at %s) - did you delete it?" % (k, self.paths[k]))


	def load_item(self, key):
		"""
			loads the specified item 
		"""
		assert key in self
		self.data[key] = self.load_funcs[key](self.paths[key])


	def save_item(self, key):
		"""
			saves the specified item 
		"""
		assert key in self
		assert not self.save_funcs[key] is None
		self.save_funcs[key](self.data[key], self.paths[key])


	def get_item(self, key):
		"""
			returns named item; loads from disk if necessary
		"""
		print key 
		print self.present_items
		if self.data[key] is None and self.item_present(key):
			self.load_item(key)
		return self.data[key]


	def set_item(self, key, value):
		"""
			sets named item; saves to disk immediately
		"""
		self.data[key] = value
		self.save_item(key)


	def del_item(self, key):
		"""
			sets self.data[key] to None, removes item 
			from disk
		"""
		self.data[key] = None
		os.remove(self.paths[key])










