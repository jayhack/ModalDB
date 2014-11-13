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
		if type(schema) == dict:
			self.schema = ModalSchema(schema)
		elif type(schema) == ModalSchema:
			self.schema = schema
		elif schema is None:
			self.schema = self.load_schema()
		else:
			raise Exception("Schema type not recongized. (Should be dict or ModalSchema)")

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
				self.ensure_dir_exists(self.get_root_type_dir(datatype))



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

	def get_schema(self, datatype):
		return self.schema[datatype]

	def get_datatypes(self):
		return set(self.schema.keys())

	def is_valid_datatype(self, datatype):
		return datatype in self.get_datatypes()

	def get_collection(self, datatype):
		assert self.is_valid_datatype(datatype)
		return self.db[datatype.__name__]

	def get_childtypes(self, datatype):
		assert self.is_valid_datatype(datatype)
		if not 'contains' in self.get_schema(datatype):
			return set([])
		else:
			return set(self.schema[datatype]['contains'])

	def get_item_names(self, datatype):
		return set(self.get_schema(datatype).keys()).difference(set(['contains']))

	def get_item_filename(self, datatype, key):
		assert self.is_valid_datatype(datatype)
		return self.get_schema(datatype)[key]['filename']

	def is_leaf_type(self, datatype):
		return len(self.get_childtypes(datatype)) == 0

	def get_root_types(self):
		ds = self.get_datatypes()
		return ds.difference(set.union(*[self.get_childtypes(d) for d in ds]))

	def is_root_type(self, datatype):
		return datatype in self.get_root_types()

	def get_root_type_dir(self, datatype):
		return os.path.join(self.root, datatype.__name__)





	####################################################################################################
	######################[ --- GET/ITER --- ]##########################################################
	####################################################################################################

	def mongo_doc_to_dataobject(self, datatype, mongo_doc):
		return datatype(mongo_doc, self.get_schema(datatype), self)

	def get(self, datatype, _id):
		"""
			returns object of type datatype and named _id
		"""
		mongo_doc = self.get_collection(datatype).find_one({'_id':_id})
		if not mongo_doc:
			raise KeyError("No such object in DB")
		return self.mongo_doc_to_dataobject(datatype, mongo_doc)


	def iter(self, datatype):
		"""
			iterates through all objects of given datatype
		"""
		cursor = self.get_collection(datatype).find()
		for i in xrange(cursor.count()):
			yield self.mongo_doc_to_dataobject(datatype, cursor.next())






	####################################################################################################
	######################[ --- INSERTING --- ]#########################################################
	####################################################################################################

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


	def sanitize_item_data(self, datatype, item_data):
		"""
			sanitizes item_data:
				- no items that don't exist in datatype's schema
				- all other items get set to None
		"""
		#=====[ Step 1: must be a dict	]=====
		if not type(item_data) == dict:
			raise TypeError("item_data must be a dict")

		all_items 		= self.get_item_names(datatype)
		named_items 	= set(item_data.keys())
		outside_items 	= named_items.difference(all_items)
		missing_items 	= all_items.difference(named_items)		

		#=====[ Step 2: no nonexistant elements	]=====
		if len(outside_items) > 0:
			raise Exception("Items don't exist for datatype %s: %s" % (datatype.__name__, str(outside_items)))

		#=====[ Step 3: fill in missing items	]=====
		for item_name in missing_items:
			item_data[item_name] = None

		#=====[ Step 3: valid paths for disk items	]=====
		for k, v in self.get_disk_items(datatype, item_data).items():
			if not v is None:
				if not os.path.exists(v):
					raise Exception("Path for item %s doesn't exist: %s" % (k, v))

		return item_data


	def ensure_dir_exists(self, path):
		if not os.path.exists(path):
			os.mkdir(path)


	def create_object_dir(self, datatype, root, item_data, method):
		"""
			creates a directory to contain all disk items for this
			object at root
		"""
		#=====[ Step 1: create root directory (DONT OVERWRITE)	]=====
		self.ensure_dir_exists(root)

		#=====[ Step 2: create subdirectories for child datatypes	]=====
		for d in self.get_childtypes(datatype):
			self.ensure_dir_exists(os.path.join(root, d.__name__))

		#=====[ Step 3: (cp|mv) disk items	]=====
		schema = self.get_schema(datatype)
		for key, old_path in self.get_disk_items(datatype, item_data).items():

			#=====[ Case: user didn't specify	]=====
			if old_path is None:
				continue

			new_path = os.path.join(root, self.get_item_filename(datatype, key))

			#=====[ Case: same path	]=====
			if os.path.exists(new_path):
				if os.path.samefile(old_path, new_path):
					continue

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
		mongo_doc['children'] = {c.__name__:{} for c in self.get_childtypes(datatype)}

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
		schema = self.get_schema(datatype)

		#=====[ Step 1: sanitize datatype/_id/method	]=====
		assert self.is_valid_datatype(datatype)
		assert type(_id) in [str, unicode]
		assert method in ['cp', 'mv']
		
		#=====[ Step 2: sanitize item data	]=====
		item_data = self.sanitize_item_data(datatype, item_data)

		#=====[ Step 3: get root directory, _id from parent	]=====
		if parent is None:
			parent_dir = self.get_root_type_dir(datatype)
			root = os.path.abspath(os.path.join(parent_dir, _id))
		else:
			parent_dir = parent.get_child_dir(datatype)
			root = os.path.join(parent_dir, _id)
			_id = parent._id + '/' + _id

		#=====[ Step 4: create object dir	]=====
		self.create_object_dir(datatype, root, item_data, method)

		#=====[ Step 5: create + insert mongo doc	]=====
		mongo_doc = self.create_mongo_doc(datatype, _id, root, item_data)
		self.get_collection(datatype).insert(mongo_doc)

		#=====[ Step 6: add to parent, if necessary	]=====
		if not parent is None:
			parent.add_child(datatype, _id)

		#=====[ Step 7: create and return datatype	]=====
		return datatype(mongo_doc, schema, self)






