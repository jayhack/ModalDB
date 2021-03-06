'''
Test: ModalSchema
=================

Description:
------------
	
	Contains functionality for dealing with and interpreting 
	ModalDB schemas


##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
import os
import unittest 
import nose
from copy import copy, deepcopy
from nose.tools import *
from scipy.io import loadmat, savemat
from scipy.misc import imsave, imread
from ModalDB import *
from schema_example import schema_ex

class Test_ModalSchema(unittest.TestCase):

	################################################################################
	####################[ setUp	]###################################################
	################################################################################

	def setUp(self):
		self.schema_ex = schema_ex
		
	def tearDown(self):
		pass




	################################################################################
	####################[ Creation	]###############################################
	################################################################################

	def test_creation_1(self):
		"""
			BASIC CREATION TEST
			-------------------
			merely constructs a ModalSchema
		"""
		schema = ModalSchema(deepcopy(self.schema_ex))
		self.assertTrue(type(schema.schema_dict) == dict)
		self.assertTrue('filename' in schema.schema_dict[Frame]['image']) 
		self.assertTrue(schema.schema_dict[Frame]['image']['filename'] == 'image.png')
		self.assertTrue(not 'filename' in schema.schema_dict[Video]['summary'])


	@raises(TypeError)
	def test_creation_2(self):
		"""
			TOP LEVEL KEYS AS STRINGS
			-------------------------
			should raise a TypeError due to top-level keys being 
			strings
		"""
		schema = deepcopy(self.schema_ex)
		schema['Frame'] = schema[Frame]
		schema['Video'] = schema[Video]
		del schema[Frame]
		del schema[Video]
		ModalSchema(schema)


	@raises(TypeError)
	def test_creation_3(self):
		"""
			DISK-ITEM WITHOUT LOAD_FUNC
			---------------------------
			should raise a TypeError due to disk-items not specifying 
			load functions
		"""
		schema = deepcopy(self.schema_ex)
		del schema[Frame]['image']['load_func']
		ModalSchema(schema)


	@raises(TypeError)
	def test_creation_4(self):
		"""
			LOAD_FUNC WITH INCORRECT # OF ARGS 
			----------------------------------
			should raise a TypeError due to load_funcs with improper 
			# of arguments
		"""
		schema = deepcopy(self.schema_ex)
		schema[Frame]['image']['load_func'] = lambda x, p: imread(p)
		ModalSchema(schema)


	@raises(TypeError)
	def test_creation_5(self):
		"""
			SAVE_FUNC WITH INCORRECT # OF ARGS 
			----------------------------------
			should raise a TypeError due to load_funcs with improper 
			# of arguments
		"""
		schema = deepcopy(self.schema_ex)
		schema[Frame]['image']['save_func'] = lambda p: imsave(p)
		ModalSchema(schema)


	@raises(TypeError)
	def test_creation_6(self):
		"""
			SAVE_FUNC WITH INCORRECT SCHEMA 
			-------------------------------
			should raise a TypeError due to 'Nesting' being improperly
			formatted
		"""
		schema = deepcopy(self.schema_ex)
		schema['Nesting'] = {Video:Frame}
		ModalSchema(schema)


	@raises(TypeError)
	def test_creation_7(self):
		"""
			SAVE_FUNC WITH INCORRECT SCHEMA 
			-------------------------------
			should raise a TypeError due to 'Nesting' being improperly
			formatted
		"""
		schema = deepcopy(self.schema_ex)
		schema['Nesting'] = ['Video', 'Frame']
		ModalSchema(schema)





	################################################################################
	####################[ Modification	]###########################################
	################################################################################

	def test_add_item_1(self):
		"""
			ADD ITEM TO FRAME
			-----------------
			should perfectly add an item to the frame 
		"""
		schema = ModalSchema(deepcopy(self.schema_ex))
		item_dict = {
						'mode':'disk',
						'filename':'depth_image.mat',
						'load_func':lambda p: loadmat(p),
						'save_func':lambda x, p: savemat(x, p)
					}
		schema.add_item(Frame, 'depth_image', item_dict)
		self.assertTrue('depth_image' in schema.schema_dict[Frame])
		self.assertTrue('filename' in schema.schema_dict[Frame]['depth_image']) 
		self.assertTrue(schema.schema_dict[Frame]['depth_image']['filename'] == 'depth_image.mat')


	def test_delete_item_1(self):
		"""
			REMOVE ITEM FROM FRAME
			----------------------
			should remove an item from Frame in the schema
		"""
		schema = ModalSchema(deepcopy(self.schema_ex))
		schema.delete_item(Frame, 'subtitles')
		self.assertFalse('depth_image' in schema.schema_dict[Frame])


	
	################################################################################
	####################[ Load and Save	]###########################################
	################################################################################

	def test_load_save(self):
		"""
			LOADING AND SAVING 
			------------------
			save then reload the schema 
		"""
		ModalSchema(deepcopy(self.schema_ex)).save('./tests/schema_temp.pkl')
		schema = ModalSchema('./tests/schema_temp.pkl')
		self.assertTrue(type(schema.schema_dict) == dict)
		self.assertTrue('filename' in schema.schema_dict[Frame]['image']) 
		self.assertTrue(schema.schema_dict[Frame]['image']['filename'] == 'image.png')
		self.assertTrue(not 'filename' in schema.schema_dict[Video]['summary'])
		os.remove('./tests/schema_temp.pkl')




