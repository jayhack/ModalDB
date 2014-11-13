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

class ChildContainer(object):
	"""
		Class: ChildContainer
		=====================
		facilitates interaction with a DataObject's children.
		wraps around a document stored in MongoDB

		Terminology:
		------------
		raw_id: _id of child in isolation, i.e. 'frame_1'
		full_id: _id of child given its parent, i.e. 'video_1/frame_1'

	"""
	id_joiner = '/'

	def __init__(self, parent_id, mongo_doc):
		""""
			mongo_doc: document containing a DataObject
		"""
		self.parent_id = parent_id
		self.parent_prefix = parent_id + self.id_joiner
		self.childtype_dicts = mongo_doc['children']




	################################################################################
	####################[ UTILS	]###################################################
	################################################################################

	def get_childtypes(self):
		return self.childtype_dicts.keys()

	def is_valid_childtype(self, datatype):
		return datatype.__name__ in self.get_childtypes()

	def get_only_childtype(self):
		if not len(self.get_childtypes) == 1:
			raise Exception("You need to specify the child's datatype")
		return self.get_childtypes()[0]

	def is_full_id(self, _id):
		return _id.startswith(self.parent_prefix)

	def is_raw_id(self, _id):
		return not self.is_full(_id)

	def to_raw_id(self, _id):
		_id = str(_id)
		if self.is_raw_id(_id):
			return _id[len(self.parent_prefix):]
		return _id

	def to_full_id(self, _id):
		_id = str(_id)
		if self.is_full_id(_id):
			return self.parent_prefix + _id
		return _id

	def get_childtype_dict(self, datatype):
		assert self.is_valid_childtype(datatype)
		return self.childtype_dicts[datatype.__name__]



	################################################################################
	####################[ GET/ADD	]###############################################
	################################################################################

	def get_child(self, **args):
		"""
			Args:
			-----
			- (Optional, first): childtype (can omit if there's only one)
			- id of child; can be either full or raw
		"""
		assert len(args) in [1, 2]

		#=====[ Case: only one childtype	]=====
		if len(args) == 1:
			return self.get_child(self.get_only_childtype(), args[0])

		#=====[ Case: >= 1 childtypes	]=====
		elif len(args) == 2:
			return self.get_childtype_dict(args[0])[self.to_raw_id(args[1])]


	def add_child(self, **args):
		"""
			Args:
			-----
			- (Optional, first): childtype (can omit if there's only one)
			- id of child; can be either full or raw
		"""
		assert len(args) in [1, 2]

		#=====[ Step 1: get childtype, _id	]=====
		if len(args) == 1:
			childtype, _id = self.get_only_childtype(), args[0]
			_id = args[1]
		elif len(args) == 2:
			childtype, _id = args[0], args[1]

		#=====[ Step 2: insert 	]=====
		raw_id, full_id = self.to_raw_id(_id), self.to_full_id(_id)
		childtype_dict = self.get_childtype_dict(childtype)
		childtype_dict[raw_id] = full_id







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

		children:
		---------
		children may be identified to their parent differently than they 
		are globally. For example, the frame '1' in a video 'myvid' is '1'
		its parent, while it's known as 'myvid/Frame/1' globally.


	"""
	def __init__(self, mongo_doc, schema, client):
		"""
			Args:
			-----
			- mongo_doc: dict containing root, in-memory items
			- schema: dict containing schema for this object
			- client: reference to ModalClient object
		"""
		self._id = mongo_doc['_id']
		self.root = mongo_doc['root']
		self.schema = schema
		self.client = client
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

	def get_child_dict(self, datatype):
		return self.children[datatype.__name__]

	def get_child_ids(self, datatype):
		assert self.is_child_type(datatype)
		return self.get_child_dict(datatype).keys()

	def get_raw_child_id(self, _id):
		return '/'.split(_id)[-1]

	def get_child_dir(self, datatype):
		assert self.is_child_type(datatype)
		return os.path.join(self.root, datatype.__name__)

	def add_child(self, datatype, _id):
		assert self.is_child_type(datatype)
		self.get_child_dict(datatype)[self.get_raw_child_id(_id)] = _id
		out = self.client.get_collection(type(self)).update(
					{'_id':self._id}, 
					{'$set':{'children':self.children}},
					upsert=False
		)

	def get_child(self, datatype, raw_child_id):
		"""
			Grab a child DataObject by *index*
		"""
		assert self.is_child_type(datatype)
		type_children = self.get_child_dict(datatype)
		raw_child_id = str(raw_child_id)
		if not raw_child_id in type_children.keys():
			raise KeyError("No such child exists: %s", raw_child_id)
		return self.client.get(datatype, type_children[raw_child_id])

	def iter_children(self, datatype):
		for child_id in self.get_child_ids():
			yield self.get_child(self, datatype)







