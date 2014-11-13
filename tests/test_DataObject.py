'''
Test: DataObject
================

Description:
------------
	
	Makes sure that multi-modal data access is working


##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
import os
import shutil

import unittest
import nose
from copy import copy, deepcopy
from nose.tools import *
from scipy.io import loadmat, savemat
from scipy.misc import imsave, imread

from ModalDB.DataObject import DataObject
from ModalDB import Video, Frame

from schema_example import schema_ex

class Test_DataObject(unittest.TestCase):

	################################################################################
	####################[ setUp	]###################################################
	################################################################################

	root = os.path.join(os.path.split(__file__)[0], 'data_ModalDicts')
	image_path = os.path.join(root, 'image.png')
	image_backup_path = os.path.join(root, 'image.backup.png')

	def reset_image(self):
		shutil.copy(self.image_backup_path, self.image_path)

	def image_exists(self):
		return os.path.exists(self.image_path)

	def remove_image(self):
		if self.image_exists():
			os.remove(self.image_path)

	def setUp(self):
		"""
			creates basic schema 
		"""
		self.reset_image()

		#=====[ Step 2: Schema 	]=====
		self.schema_ex = schema_ex

		#=====[ Step 3: Mongo Doc	]=====
		self.mongo_doc = {	
							'_id':'12345',
							'root':self.root,
							'items':{
										'image':{
													'present':True,
												},
										'subtitles':{
													'present':True,
													'data':'hello, world!'
												}
									},
							'children':{}
						}


	def tearDown(self):
		self.remove_image()




	################################################################################
	####################[ ITEM ACCESS TESTS	]#######################################
	################################################################################

	def test_creation(self):
		"""
			BASIC CREATION
			--------------
			merely constructs a DataObject
		"""
		d = DataObject(deepcopy(self.mongo_doc), self.schema_ex[Frame], None)


	def test_getitem(self):
		"""
			BASIC GETITEM
			-------------
			gets image and subtitles
		"""
		self.reset_image()
		d = DataObject(deepcopy(self.mongo_doc), self.schema_ex[Frame], None)
		self.assertEqual(d['image'].shape, (512, 512, 3))
		self.assertEqual(d['subtitles'], 'hello, world!')


	def test_setitem(self):
		"""
			BASIC SETITEM TEST
			------------------
			gets image and subtitles
		"""
		self.reset_image()
		d = DataObject(deepcopy(self.mongo_doc), self.schema_ex[Frame], None)

		img = d['image']
		sub = d['subtitles']

		self.remove_image()
		d['image'] = img
		d['subtitles'] = 'konnichiwa, sekai!'

		self.assertTrue(self.image_exists())
		self.assertEqual(d['image'].shape, (512, 512, 3))
		self.assertEqual(d['subtitles'], 'konnichiwa, sekai!')


	def test_delitem(self):
		"""
			BASIC DELITEM TEST
			------------------
			removes both, makes sure it works
		"""
		self.reset_image()
		d = DataObject(deepcopy(self.mongo_doc), self.schema_ex[Frame], None)
		
		del d['image']
		del d['subtitles']

		self.assertTrue(d['image'] is None)
		self.assertTrue(not self.image_exists())
		self.assertTrue(d['subtitles'] is None)


	def test_update_item_metadata(self):
		"""
			BASIC ITEM METADATA UPDATE TEST 
			-------------------------------
			checks on items present, absent, etc.
		"""
		self.reset_image()
		mongo_doc = deepcopy(self.mongo_doc)
		d = DataObject(mongo_doc, self.schema_ex[Frame], None)

		self.assertTrue(mongo_doc['items']['image']['present'])
		self.assertTrue(mongo_doc['items']['subtitles']['present'])
		self.assertTrue('image' in d.present_items())
		self.assertTrue('subtitles' in d.present_items())
		self.assertTrue(len(d.present_items()) == 2)

		del d['image']
		del d['subtitles']

		self.assertFalse(mongo_doc['items']['image']['present'])
		self.assertFalse(mongo_doc['items']['subtitles']['present'])
		self.assertFalse('image' in d.present_items())
		self.assertFalse('subtitles' in d.present_items())
		self.assertTrue(len(d.present_items()) == 0)


