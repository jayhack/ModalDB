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
		self.initialize_schema()

		#=====[ Step 3: Connect to/initialize MongoDB	]=====
		self.initialize_mongodb()


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
				self.db.createCollection(root_type.__name__)


	def clear_db(self):
		"""
			erases all info that already exists in the db 
		"""
		for db_name in self.mongo_client.database_names():
			if not db_name in ['admin', 'local']:
				client.drop_database(db_name)


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
		for cname in self.db.collection_names():
			collection = self.db[cname]
			cursor = collection.find()
			for _ in range(collection.count()):
				obj = cursor.next()
				obj.validate_filesystem()



	####################################################################################################
	######################[ --- INSERTING ELEMENTS --- ]################################################
	####################################################################################################

	def get_root_types(self):
		"""
			returns set of root types
		"""
		return set(self.schema['Nesting'][0])


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


	def create_mongo_doc(self, _id, root, data_type):
		"""
			creates a mongodb document representing a given data type 
		"""
		schema = self.schema[data_type]
		mongo_doc = {}

		#=====[ Step 1: fill in root	]=====
		mongo_doc['root'] = root

		#=====[ Step 2: fill in name	]=====
		mongo_doc['_id'] = _id

		#=====[ Step 3: fill mongo_doc['items'] ]=====
		mongo_doc['items'] = deepcopy(schema)
		for k,v in mongo_doc['items']:
			v['exists'] = False

		#=====[ Step 4: fill mongo_doc['children']	]=====
		mongo_doc['children'] = {}

		#=====[ Step 5: fill type and child_type	]=====
		mongo_doc['datatype'] = data_type
		mongo_doc['child_type'] = self.get_child_type(data_type)

		return mongo_doc


	def insert_object(self, _id, data_type, method='cp'):
		"""
			inserts top-level objects into the DB

			name: name of this object (becomes _id)
			data_type: subclass of DataObject

			method: cp or mv 
					- cp: copies the file 
					- mv: moves the file

		"""
		#=====[ Step 1: sanitize input	]=====
		if not issubclass(data_type, DataObject):
			raise Exception("Inserted object must be a subclass of DataObject")
		if not self.is_root_type(data_type):
			raise Exception("Inserted object must be one of the root types")
		if not method in ['cp', 'mv']:
			raise Exception("Only supported insertion modes are 'cp' and 'mv'")


		#=====[ Step 2: create corresponding mongo_doc 	]=====
		mongo_doc = self.create_mongo_doc(_id, root, data_type)




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





