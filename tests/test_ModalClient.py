"""
Test: ModalClient
=================

Description:
------------
	
	Puts ModalClient through tests involving:
		- loading and saving schemas
		- inserting data objects



##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
"""
import os
import dill as pickle
import unittest 
from copy import copy, deepcopy
import nose
from nose.tools import *
from scipy.io import loadmat, savemat
from scipy.misc import imsave, imread

from ModalDB import *

from schema_example import schema_ex
from dataobject_example import video_data, frame_data, data_dir

class Test_ModalSchema(unittest.TestCase):

	################################################################################
	####################[ setUp	]###################################################
	################################################################################

	thumbnail_backup_path = os.path.join(data_dir, 'thumbnail.backup.png')
	thumbnail_path = os.path.join(data_dir, 'thumbnail.png')
	image_backup_path = os.path.join(data_dir, 'image.backup.png')
	image_path = os.path.join(data_dir, 'image.png')
	schema_path = os.path.join(data_dir, '.ModalDB_schema.pkl')


	def reset_images(self):
		shutil.copy(thumbnail_backup_path, thumbnail_path)
		shutil.copy(image_backup_path, image_path)


	def setUp(self):

		self.schema = ModalSchema(schema_ex)
		self.video_data = video_data
		self.frame_data = frame_data
		self.schema.save(self.schema_path)
		self.reset_images()


	def tearDown(self):
		pass






	################################################################################
	####################[ CREATION	]###############################################
	################################################################################

	def test_creation_1(self):
		"""
			BASIC CREATION PASSING IN SCHEMA
			--------------------------------
			merely constructs a ModalClient, loading the schema
		"""
		client = ModalClient(root=self.data_dir, schema=self.schema)


	def test_creation_2(self):
		"""
			BASIC CREATION LOADING DEFAULT SCHEMA
			-------------------------------------
			merely constructs a ModalClient, loading the schema
		"""
		client = ModalClient(root=self.data_dir)
		schema = client.schema
		self.assertTrue(type(schema.schema_dict) == dict)
		self.assertTrue('filename' in schema.schema_dict[Frame]['image']) 
		self.assertTrue('filename' in schema.schema_dict[Frame]['skeleton']) 
		self.assertTrue(schema.schema_dict[Frame]['image']['filename'] == 'image')
		self.assertTrue(not 'filename' in schema.schema_dict[Video]['subtitles'])





	################################################################################
	####################[ DATA INSERTION	]#######################################
	################################################################################

	def test_insertion_cp(self):
		"""
			BASIC INSERTION OF VIDEO AND FRAME (CP)
			---------------------------------------
			constructs a video and a frame, inserts them via CP 
		"""
		client = ModalClient(root=self.data_dir)
		video = client.insert(Video, 'test_video', self.video_data, method='cp')
		frame = client.insert(Frame, 'test_frame', self.frame_data, parent=frame, method='cp')


	


