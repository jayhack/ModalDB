'''
Class: ModalClient
==================

Description:
------------
	
	Main class for interfacing with the MongoClient


##############
Jay Hack
Fall 2014
jhack@stanford.edu
##############
'''
import os
import shutil
import random
import dill as pickle
from copy import copy, deepcopy
from itertools import islice
from pprint import pformat, pprint
from pymongo import MongoClient

from ModalSchema import ModalSchema
from Video import Video


class ModalClient(object):
	"""
		Example Usage:
		--------------

		# Initialization
		mc = ModalClient(Schema)

		# Accessing videos 
		video = mc.get_video('...')
		for video in mc.iter_videos():
			...

		# Directly Accessing Frames
		for frame in mc.iter_frames():
			...

	"""

	def __init__(self, root=os.environ['DATA_DIR'], schema=None):
		"""
			Connect to MongoDB, load schema, find root path
		"""
		self.root = root
		self.initialize_schema(schema)
		self.initialize_mongodb()





	####################################################################################################
	######################[ --- SCHEMA --- ]############################################################
	####################################################################################################
	
	def initialize_schema(self, schema):
		"""
			sets self.schema
			if schema is None, loads default one from disk.
		"""
		#=====[ Step 1: Set schema path	]=====
		self.schema_path = os.path.join(self.root, '.ModalDB_schema.pkl')

		#=====[ Step 2: Load schema	]=====
		if not schema is None:
			self.schema = schema
		else:
			self.schema = self.load_schema()

	def load_schema(self):
		if not os.path.exists(self.schema_path):
			raise Exception("No schema exists or was specified")
		return ModalSchema(self.schema_path)

	def save_schema(self):
		self.schema.save(self.schema_path)

	def print_schema(self):
		pprint(self.schema.schema_dict)







	####################################################################################################
	######################[ --- MONGODB --- ]###########################################################
	####################################################################################################


	def initialize_mongodb(self):
		"""
			starts mongodb; ensures proper collections exist;
		"""
		#=====[ Step 1: Connect	]=====
		try:
			self.mongo_client = MongoClient()
			self.db = self.mongo_client.ModalDB
		except:
			raise Exception("Turn on MongoDB.")
		
		#=====[ Step 2: Ensure collections/dirs exist	]=====
		for datatype in self.get_datatypes():

			#=====[ Collections	]=====
			if not datatype.__name__ in self.db.collection_names():
				self.db.create_collection(datatype.__name__)

			#=====[ Dirs	]=====
			if self.is_root_type(datatype):
				if not os.path.exists(self.get_root_type_dir(datatype)):
					os.mkdir(self.get_root_type_dir(datatype))



	def clear_db(self):
		"""
			drops old database and creates a new one
		"""
		for db_name in self.mongo_client.database_names():
			if not db_name in ['admin', 'local']:
				self.mongo_client.drop_database(db_name)
		self.db = self.mongo_client.ModalDB




	####################################################################################################
	######################[ --- UTILS --- ]#############################################################
	####################################################################################################

	def get_datatypes(self):
		return set(self.schema.keys())

	def is_valid_datatype(self, datatype):
		return datatype in self.get_datatypes()

	def get_children_datatypes(self, datatype):
		assert self.is_valid_datatype(datatype)
		if not 'contains' in self.schema[datatype]:
			return set([])
		else:
			return set(self.schema[datatype]['contains'])

	def is_leaf_type(self, datatype):
		return len(self.get_children_datatypes(datatype)) == 0

	def get_root_types(self):
		ds = self.get_datatypes()
		return ds.difference(set.union(*[self.get_children_datatypes(d) for d in ds]))

	def is_root_type(self, datatype):
		return datatype in self.get_root_types()

	def get_collection(self, datatype):
		return self.db[datatype.__name__]

	def get_schema(self, datatype):
		return self.schema[datatype]

	def get_root_type_dir(self, datatype):
		return os.path.join(self.root, datatype.__name__)


	####################################################################################################
	######################[ --- GETTING/INSERTING --- ]#################################################
	####################################################################################################

	def get(self, datatype, _id):
		"""
			returns object of type datatype and named _id
		"""
		assert self.is_valid_datatype(datatype)
		mongo_doc = self.get_collection(datatype).find_one({'_id':_id})
		schema = self.get_schema(datatype)
		return datatype(mongo_doc, schema)


	def get_disk_items(self, datatype, item_data):
		"""
			returns portion of item_data describing disk items 
		"""
		return {k:v for k,v in item_data.items() if self.get_schema(datatype)[k]['mode'] == 'disk'}


	def get_memory_items(self, datatype, item_data):
		"""
			returns portion of item_data describing memory items 
		"""
		return {k:v for k,v in item_data.items() if self.get_schema(datatype)[k]['mode'] == 'memory'}


	def create_object_dir(self, datatype, root, item_data, method):
		"""
			creates a directory to contain all disk items for this
			object at root
		"""
		#=====[ Step 1: create root directory	]=====
		if os.path.exists(root):
			shutil.rmtree(root)
		os.mkdir(root)

		#=====[ Step 2: create subdirectories for children	]=====
		for d in self.get_children_datatypes(datatype):
			path = os.path.join(root, d.__name__)
			if not os.path.exists(path):
				os.mkdir(path)

		#=====[ Step 3: get disk items	]=====
		schema = self.get_schema(datatype)
		disk_items = self.get_disk_items(datatype, item_data)

		#=====[ Step 4: copy items	]=====
		for key,old_path in disk_items.items():
			filename = schema[key]['filename']
			new_path = os.path.join(root, filename)

			#=====[ Case: cp	]=====
			if method == 'cp':
				shutil.copy2(old_path, new_path)

			#=====[ Case: mv	]=====
			elif method == 'mv':
				shutil.move(old_path, new_path)



	def create_mongo_doc(self, datatype, _id, root, item_data):
		"""
			returns doc that can be inserted into a mongodb collection
			to represent this item.
		"""
		#=====[ Step 1: get disk/memory items	]=====
		schema = self.get_schema(datatype)
		disk_items = self.get_disk_items(datatype, item_data)
		memory_items = self.get_memory_items(datatype, item_data)

		#=====[ Step 2: basic mongo_doc	]=====
		mongo_doc = {
						'root':root,
						'_id':_id,
					}

		#=====[ Step 3: mongo_doc['items']	]=====
		mongo_doc['items'] = {}
		for k in disk_items.keys():
			mongo_doc['items'][k] = {'present':None}
		for k,v in memory_items.items():
			mongo_doc['items'][k] = {'present':True, 'data':item_data[k]}

		#=====[ Step 4: mongo_doc['children']	]=====
		children = self.get_children_datatypes(datatype)
		if len(children) > 0:
			mongo_doc['children'] = {c.__name__:[] for c in children}

		return mongo_doc



	def insert(self, datatype, _id, item_data, parent=None, method='cp'):
		"""
			creates/inserts new dataobject, returns it.

			Args:
			-----
			- datatype: type of object to create
			- _id: name of object to create 
			- item_data: dict containing info on objects
			- method: (cp or mv) copy or move files 

			item_data details:
			------------------
			for memory items: name maps to *contents*
			for disk items: name maps to *current filepath*

			item_data ex:
			-------------
			{
				'subtitles':'hello, world!',
				'image':'/path/to/image.png',
			}
		"""
		#=====[ Step 1: sanitize datatype/_id/method	]=====
		assert self.is_valid_datatype(datatype)
		assert type(_id) in [str, unicode]
		assert method in ['cp', 'mv']
		
		#=====[ Step 2: sanitize item data	]=====
		assert type(item_data) == dict 
		schema = self.get_schema(datatype)
		for k, v in item_data.items():
			assert k in schema
			if schema[k]['mode'] == 'disk':
				assert os.path.exists(v)

		#=====[ Step 3: get root directory	]=====
		if parent is None:
			parent_dir = self.get_root_type_dir(datatype)
		else:
			parent_dir = parent.get_child_dir(datatype)
		root = os.path.join(parent_dir, _id)

		#=====[ Step 4: create object dir	]=====
		self.create_object_dir(datatype, root, item_data, method)

		#=====[ Step 5: create + insert mongo doc	]=====
		mongo_doc = self.create_mongo_doc(datatype, _id, root, item_data)
		self.get_collection(datatype).insert(mongo_doc)

		#=====[ Step 6: add to parent, if necessary	]=====
		if not parent is None:
			parent.add_child(datatype, _id)

		#=====[ Step 7: create and return datatype	]=====
		return datatype(mongo_doc, schema)






