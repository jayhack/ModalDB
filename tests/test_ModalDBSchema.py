'''
Test: ModalDBSchema
===================

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
import unittest 
import nose
from copy import copy, deepcopy
from nose.tools import *
from scipy.io import loadmat, savemat
from scipy.misc import imsave, imread
from ModalDB import *

class Test_ModalDBSchema(unittest.TestCase):

	################################################################################
	####################[ setUp	]###################################################
	################################################################################

	def setUp(self):
		"""
			creates basic schema 
		"""
		self.schema_ex = {
							'Nesting':{Video:{Frame}},

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
						}






	################################################################################
	####################[ Creation	]###############################################
	################################################################################

	def test_creation_1(self):
		"""
			BASIC CREATION TEST
			-------------------
			merely constructs a ModalDBSchema
		"""

		schema = ModalDBSchema(deepcopy(self.schema_ex))
		self.assertTrue(type(schema.schema_dict) == dict)
		self.assertTrue('filename' in schema.schema_dict[Frame]['image']) 
		self.assertTrue('filename' in schema.schema_dict[Frame]['skeleton']) 
		self.assertTrue(schema.schema_dict[Frame]['image']['filename'] == 'image')
		self.assertTrue(not 'filename' in schema.schema_dict[Video]['subtitles'])


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
		ModalDBSchema(schema)


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
		del schema[Frame]['skeleton']['load_func']		
		ModalDBSchema(schema)


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
		schema[Frame]['skeleton']['load_func'] = lambda x, p: loadmat(p)
		ModalDBSchema(schema)


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
		ModalDBSchema(schema)







	################################################################################
	####################[ Modification	]###########################################
	################################################################################

	def test_add_item_1(self):
		"""
			ADD ITEM TO FRAME
			-----------------
			should perfectly add an item to the frame 
		"""
		schema = ModalDBSchema(deepcopy(self.schema_ex))
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



