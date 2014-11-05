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

	def __init__(self, schema=None):
		"""
			Connect to MongoDB, load schema, find root path
		"""
		#=====[ Step 1: Grab root from envvars	]=====
		self.root = os.environ['DATA_DIR']
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
				raise Exception("You need to specify a schema! See ModalSchema")





	####################################################################################################
	######################[ --- DATABASE MANIPULATION --- ]#############################################
	####################################################################################################

	def reset_db(self):
		"""
			erases all info that already exists in the db 
		"""
		for db_name in self.mongo_client.database_names():
			if not db_name in ['admin', 'local']:
				client.drop_database(db_name)




	####################################################################################################
	######################[ --- SCHEMA --- ]############################################################
	####################################################################################################
	
	def load_schema(self):
		"""
			loads the schema from $DATA_DIR/.ModalDB_schema.pkl
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
		raise NotImplementedError




	####################################################################################################
	######################[ --- VIDEO ACCESS --- ]######################################################
	####################################################################################################

	@property
	def videos(self):
		"""
			Access to the videos table
		"""
		return self.db.videos

	@videos.setter
	def videos(self, value):
		self.db.videos = value
	

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





