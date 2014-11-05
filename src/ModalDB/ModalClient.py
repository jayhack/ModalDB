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

		#=====[ Step 2: Connect to MongoDB	]=====
		try:
			self.mongo_client = MongoClient()
			self.db = self.mongo_client.ModalDB
		except:
			raise Exception("Turn on MongoDB.")

		#=====[ Step 3: Load Schema	]=====
		if not schema is None:
			self.schema = schema
		else:
			try:
				self.schema = self.load_schema()
			except:
				raise Exception("You need to specify a schema! (or schema doesn't yet exist) See ModalSchema")




	####################################################################################################
	######################[ --- SCHEMA --- ]############################################################
	####################################################################################################
	
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
	######################[ --- DATABASE MANIPULATION --- ]#############################################
	####################################################################################################

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



	####################################################################################################
	######################[ --- INSERTING ELEMENTS --- ]################################################
	####################################################################################################

	def get_parent_type(self, datatype):
		"""
			returns the parent type, according to self.schema 
			NOTE: currently assumes that 'Nesting' is a list, where each 
					element is a type.
		"""
		index = self.schema['Nesting'].index(datatype)
		if index == 0:
			return None 
		else:
			return self.schema['Nesting'][index - 1]



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

		return mongo_doc




	def insert_object(self, _id, parent_name, data_type, method='cp'):
		"""
			name: name of this object (becomes _id)
			parent_name: name of containing object (optionally none for top-level ones)
			data_type: subclass of DataObject

			method: cp or mv 
					- cp: copies the file 
					- mv: moves the file

		"""
		#=====[ Step 1: sanitize input	]=====
		if not issubclass(data_object, DataObject):
			raise Exception("Inserted object must be a subclass of DataObject")
		if not type(data_object) in self.schema.keys():
			raise Exception("Inserted object not described in current schema")
		if not method in ['cp', 'mv']:
			raise Exception("Only supported insertion modes are 'cp' and 'mv'")

		#=====[ Step 2: find parent	]=====
		parent_type = self.get_parent_type(data_type)


		#=====[ Step 3: create corresponding mongo_doc 	]=====
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






	####################################################################################################
	######################[ --- PRINTING --- ]##########################################################
	####################################################################################################

	def __str__(self):
		"""
			Returns a pprint of the frame schema 
		"""
		return '==========[ Client (Frame Storage) Schema ]==========\n %s' % pformat(self.schema)





