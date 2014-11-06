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
import random
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
		mc = ModalClient(FrameSchema)

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
		self.schema_path = os.path.join(self.root, '.ModalDB_schema.pkl')

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
		"""
		if not schema is None:
			self.schema = schema
		else:
			try:
				self.schema = self.load_schema()
			except:
				raise Exception("You need to specify a schema! (or schema doesn't yet exist) See ModalSchema")


	def load_schema(self):
		"""
			loads the schema from [self.root]/.ModalDB_schema.pkl
		"""
		return ModalSchema(self.schema_path)


	def save_schema(self):
		"""
			saves the schema to $DATA_DIR/.ModalDB_schema.pkl
		"""
		self.schema.save(self.schema_path)


	def print_schema(self):
		"""
			Displays the current schema 
		"""
		pprint(self.schema.schema_dict)







	####################################################################################################
	######################[ --- MONGODB --- ]###########################################################
	####################################################################################################

	def initialize_mongodb(self):
		"""
			sets collections, etc.
		"""
		#=====[ Step 1: Connect	]=====
		try:
			self.mongo_client = MongoClient()
			self.db = self.mongo_client.ModalDB
		except:
			raise Exception("Turn on MongoDB.")
		
		#=====[ Step 2: ensure collections are there	]=====
		for root_type in self.get_root_types():
			if not root_type.__name__ in self.db.collection_names():
				self.db.create_collection(root_type.__name__)


	def clear_db(self):
		"""
			erases all info that already exists in the db 
		"""
		for db_name in self.mongo_client.database_names():
			if not db_name in ['admin', 'local']:
				self.mongo_client.drop_database(db_name)


	def fill_mongo_index(self):
		"""
			goes through entire data dir and fills in data 
			directory
			(assumes no videos are there)
		"""
		raise NotImplementedError 


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
	######################[ --- ACCESSING ELEMENTS --- ]################################################
	####################################################################################################

	def get_object(self, data_type, _id):
		"""
			given a datatype and an _id, returns the requested 
			datatype 
			NOTE: data_type must currently be a root type
		"""
		assert self.is_root_type(data_type)
		collection = self.db[data_type.__name__]
		return data_type(collection.find_one({'_id':_id}), self.schema.schema_dict['Nesting'])



	####################################################################################################
	######################[ --- INSERTING ELEMENTS --- ]################################################
	####################################################################################################

	def get_root_types(self):
		"""
			returns set of root types
		"""
		return set([self.schema.schema_dict['Nesting'][0]])


	def is_root_type(self, data_type):
		"""
			returns true if data_type is the root type 
		"""
		return data_type in self.get_root_types()


	def get_parent_type(self, data_type):
		"""
			returns the parent type, according to self.schema 
			NOTE: currently assumes that 'Nesting' is a list, where each 
					element is a type.
		"""
		if self.is_root_type(data_type):
			return None
		else:
			return self.schema['Nesting'][self.schema['Nesting'].index(datatype) - 1]


	def get_child_type(self, data_type):
		"""
			returns the child type, according to self.schema 
			NOTE: currently assumes that 'Nesting' is a list, where each 
					element is a type.
		"""
		index = self.schema['Nesting'].index(datatype)
		if index == len(self.schema['Nesting']) - 1:
			return None 
		else:
			return self.schema['Nesting'][index + 1]


	def get_datatype_root(self, data_type):
		"""
			returns directory for a data_type
		"""
		return os.path.join(self.root, data_type.__name__)


	def get_root_object_root(self, data_type, _id):
		"""
			returns the directory for a root object named _id 
		"""
		return os.path.join(self.get_datatype_root(data_type), _id)


	def create_mongo_doc(self, data_type, _id):
		"""
			creates a mongodb document representing a given data type 
		"""
		schema = self.schema.schema_dict[data_type]
		mongo_doc = {}

		#=====[ Step 1: fill in root	]=====
		mongo_doc['root'] = self.get_root_object_root(data_type, _id)

		#=====[ Step 2: fill in name	]=====
		mongo_doc['_id'] = _id

		#=====[ Step 3: fill mongo_doc['items'] ]=====
		mongo_doc['items'] = deepcopy(schema)
		for v in mongo_doc['items'].values():
			v['exists'] = False

		#=====[ Step 4: fill mongo_doc['children']	]=====
		mongo_doc['children'] = {}

		return mongo_doc


	def create_root_object(self, data_type, _id):
		"""
			inserts top-level objects into the DB

			name: name of this object (becomes _id)
			data_type: subclass of DataObject
		"""
		#=====[ Step 1: sanitize input	]=====
		if not self.is_root_type(data_type):
			raise Exception("Inserted object must be one of the root types")

		#=====[ Step 2: create corresponding mongo_doc 	]=====
		mongo_doc = self.create_mongo_doc(data_type, _id)

		#=====[ Step 3: make the directory to hold it	]=====
		if not os.path.isdir(mongo_doc['root']):
			os.mkdir(mongo_doc['root'])

		return data_type(mongo_doc, self.schema.schema_dict['Nesting'])






	####################################################################################################
	######################[ --- VIDEO ACCESS --- ]######################################################
	####################################################################################################	

	def get_video(self, video_name):
		"""
			returns the named video (unloaded)
		""" 
		root = os.path.join(self.root, video_name)
		mongo_doc = self.videos.find_one(spec_or_id=video_name)
		return Video(self.db, mongo_doc, root)


	def get_random_video(self):
		"""
			returns a random video (unloaded)
		"""
		return self.get_video(self.videos.find_one()['_id'])


	def iter_videos(self, verbose=False):
		"""
			iterates over all videos 
		"""
		cursor = self.videos.find()
		for i in range(cursor.count()):
			v = self.get_video(cursor.next()['_id'])
			if verbose:
				print v
			yield v


	def iter_frames(self, verbose=False, subsample_rate=1):
		"""
			iterates over all frames
			verbose mode prints out the video names as well
		"""
		for v in self.iter_videos(verbose=verbose):
			for f in v.iter_frames(verbose=verbose, subsample_rate=subsample_rate):
				yield f





