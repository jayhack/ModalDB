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
	def __init__(self, mongo_doc, client):
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
		self.disk_dict = self.get_disk_dict(self.mongo_doc)
		self.nesting = client.schema.schema_dict['Nesting']
		self.client = client



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
		return {k:None for k,v in self.items.items() if v['mode'] == 'disk'}


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


	def get_child_type(self):
		"""
			returns child's type 
		"""
		self_index = self.nesting.index(type(self))
		if self_index == len(self.nesting) + 1:
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
		schema = client.schema.schema_dict[data_type]
		mongo_doc = {}

		#=====[ Step 1: make mongo_doc	]=====
		mongo_doc['root'] = os.path.join(self.root, data_type.__name__, _id)
		mongo_doc['_id'] = _id
		mongo_doc['items'] = deepcopy(schema)
		for v in mongo_doc['items'].values():
			v['exists'] = False
		if not self.client.is_leaf_type(data_type):
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

			#=====[ Step 3.2: call same for each child	]=====
			for child in self.iter_children():
				child.update()



