'''
Test: ModalClient
=================

Description:
------------
	
	Puts ModalClient through tests involving:
		- loading and saving schemas



##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
import os
import dill as pickle
import unittest 
from copy import copy, deepcopy
import nose
from nose.tools import *
from scipy.io import loadmat, savemat
from scipy.misc import imsave, imread

from ModalDB import *

class Test_ModalSchema(unittest.TestCase):

	################################################################################
	####################[ setUp	]###################################################
	################################################################################

	def setUp(self):
		"""
			creates basic schema, data dir to store it,
		"""
		#=====[ Basic schema	]=====
		self.schema = ModalSchema({
									'Nesting':[Video, Frame],

									Frame: {
												'image':{
															'mode':'disk',
															'load_func':lambda p: imread(p),
															'save_func':lambda x, p: imsave(x, p)
														},	
												'skeleton':{
															'mode':'disk',
															'load_func':lambda p: loadmat(p)
														}
											},

									Video: {

												'subtitles':{
															'mode':'memory'
															}
											}
								})

		#=====[ Save it for tests	]=====
		self.data_dir = 'tests/data'
		os.environ['DATA_DIR'] = self.data_dir
		self.schema_path = os.path.join(self.data_dir, '.ModalDB_schema.pkl')
		self.schema.save(self.schema_path)
		self.old_data_dir = os.environ['DATA_DIR']


	def tearDown(self):
		"""	
			resets everything from setUp 
		"""
		os.environ['DATA_DIR'] = self.old_data_dir






	################################################################################
	####################[ Creation	]###############################################
	################################################################################


	def test_creation_1(self):
		"""
			BASIC CREATION PASSING IN SCHEMA
			--------------------------------
			merely constructs a ModalClient, loading the schema
		"""
		client = ModalClient(schema=self.schema)



	def test_creation_2(self):
		"""
			BASIC CREATION LOADING DEFAULT SCHEMA
			-------------------------------------
			merely constructs a ModalClient, loading the schema
		"""
		client = ModalClient(root='./tests/data')
		schema = client.schema
		self.assertTrue(type(schema.schema_dict) == dict)
		self.assertTrue('filename' in schema.schema_dict[Frame]['image']) 
		self.assertTrue('filename' in schema.schema_dict[Frame]['skeleton']) 
		self.assertTrue(schema.schema_dict[Frame]['image']['filename'] == 'image')
		self.assertTrue(not 'filename' in schema.schema_dict[Video]['subtitles'])
	


