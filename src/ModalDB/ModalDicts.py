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

class DiskDict(dict):
	"""
		Class: DiskDict
		---------------
		Facilitates access to items on disk
	"""

	def __init__(self, mongo_doc, datatype_schema):
		"""
			Args:
			-----
			- mongo_doc: contains named items 
			- datatype_schema: describes *this* object's datatype
		"""
		
		root = mongo_doc['root']
		items = datatype_schema

		self.keys 		= [k for k,v in items.items() if v['mode'] == 'disk']
		self.load_funcs = {k:items[k]['load_func'] for k in self.keys}
		self.save_funcs = {k:items[k]['save_func'] for k in self.keys}
		self.paths 		= {k:os.path.join(root, items[k]['filename']) for k in self.keys}
		self.metadata 	= {k:mongo_doc['items'][k] for k in self.keys}
		self.data 		= {k:None for k in self.keys}


	def __contains__(self, key):
		return key in self.keys


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
		self.save_funcs[key](self.paths[key])


	def __getitem__(self, key):

		#=====[ Step 1: detect key errors	]=====
		if not key in self:
			raise KeyError("No such item in schema: %s" % key)

		#=====[ Step 2: load if necessary ]=====
		if self.data[key] is None:
			self.load_item(key)

		return self.data[key]


	def __setitem__(self, key):

		#=====[ Step 1: detect key errors	]=====
		if not key in self:
			raise KeyError("No such item in schema: %s" % key)

		#=====[ Step 2: load if necessary ]=====
		if self.data[key] is None:
			self.load_item(key)

		return self.data[k]











