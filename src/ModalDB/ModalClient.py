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
		#=====[ Step 1: Grab root from envvars	]=====
		self.root = root

		#=====[ Step 3: Initialize schema	]=====
		self.initialize_schema(schema)

		#=====[ Step 4: Connect to/initialize MongoDB	]=====
		self.initialize_mongodb()

		#=====[ Step 5:	Validate the filesystem ]=====
		self.validate_filesystem()





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
			self.load_schema()

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
		
		#=====[ Step 2: Ensure collections exist	]=====
		for root_type in self.get_types():
			if not root_type.__name__ in self.db.collection_names():
				self.db.create_collection(root_type.__name__)


	def clear_db(self):
		"""
			erases all info that already exists in the db 
		"""
		for db_name in self.mongo_client.database_names():
			if not db_name in ['admin', 'local']:
				self.mongo_client.drop_database(db_name)


	def validate_filesystem(self):
		"""
			Makes sure that the filesystem is properly set up 
		"""
		for data_type in self.get_root_types():

			#=====[ Step 1: make sure there is a directory for it	]=====
			if not os.path.isdir(self.get_datatype_root(data_type)):
				os.mkdir(self.get_datatype_root(data_type))

			collection = self.db[data_type.__name__]
			cursor = collection.find()
			for _ in range(collection.count()):
				obj_doc = cursor.next()
				obj = self.get_object(data_type, obj_doc['_id'])





	####################################################################################################
	######################[ --- GETTING ELEMENTS --- ]##################################################
	####################################################################################################

	def get_datatypes(self):
		return self.schema.keys()

	def is_valid_datatype(self, datatype):
		return datatype in self.get_datatypes()

	def get_children_datatypes(self, datatype):
		assert self.is_valid_datatype(datatype)
		return self.schema[datatype]['contains']

	def get_collection(self, datatype):
		return self.db[datatype.__name__]

	def get_schema(self, datatype):
		return self.schema[datatype]

	def get(self, datatype, _id):
		"""
			returns object of type datatype and named _id
		"""
		assert self.is_valid_datatype(datatype)
		collection = self.get_collection(datatype).find_one({'_id':_id})
		schema = self.get_schema(datatype)
		return datatype(mongo_doc, schema)





	####################################################################################################
	######################[ --- INSERTING ELEMENTS --- ]################################################
	####################################################################################################

	def get_disk_items(datatype, item_data):
		"""
			returns portion of item_data describing disk items 
		"""
		return {k:v for k,v in item_data.items() if self.get_schema(datatype)['items'][k]['mode'] == 'disk'}


	def get_memory_items(datatype, item_data):
		"""
			returns portion of item_data describing memory items 
		"""
		return {k:v for k,v in item_data.items() if self.get_schema(datatype)['items'][k]['mode'] == 'memory'}


	def create_object_dir(self, datatype, root, item_data, method):
		"""
			creates a directory to contain all disk items for this
			object at root
		"""
		#=====[ Step 1: create root directory	]=====
		if os.path.exists(root):
			os.path.remove(root)
		os.mkdir(root)

		#=====[ Step 2: get disk items	]=====
		schema = self.get_schema(datatype)
		disk_items = self.get_disk_items(datatype, item_data)

		#=====[ Step 3: copy items	]=====
		for name,old_path in disk_items.items():
			filename = schema['items'][name]['filename']
			new_path = os.path.join(root, filename)

			#=====[ Case: cp	]=====
			if method == 'cp':
				shutil.copy2(old_path, new_path)
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
		for k,v in memory_items.values():
			mongo_doc['items'][k] = {'present':True, 'data':item_data}

		#=====[ Step 4: mongo_doc['children']	]=====
		children_datatypes = self.get_children_datatypes(datatype)



		return mongo_doc



	def insert(self, datatype, _id, item_data, method='cp'):
		"""
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
			assert k in schema['items']
			if schema['items'][k]['mode'] == 'disk':
				assert os.path.exists(v)


		#=====[ Step 3: get root directory	]=====
		raise NotImplementedError

		#=====[ Step 4: create object dir	]=====
		self.create_object_dir(datatype, root, item_data, method)

		#=====[ Step 5: create + insert mongo doc	]=====
		mongo_doc = self.create_mongo_doc(data_type, _id, root, )

		#=====[ Step 3: validate filesystem	]=====
		if not parent is None:
			parent['children'].append(obj)
			parent.update()

		else:
			obj.update()
			self.db[data_type.__name__].insert(mongo_doc)



	def update(self):
		"""
			fills the db from its root directory
		"""
		root_type = self.schema.schema_dict['Nesting'][0]
		d = os.path.join(self.root, root_type.__name__)
		for _id in [x for x in os.listdir(d) if not x.startswith('.')]:
			self.insert_object(root_type, None, _id)



