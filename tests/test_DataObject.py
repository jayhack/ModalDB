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

class Test_DataObject(unittest.TestCase):

	################################################################################
	####################[ setUp	]###################################################
	################################################################################

	def setUp(self):
		"""
			creates basic schema 
		"""
		self.root = os.path.join(os.path.split(__file__)[0], 'data_ModalDicts')
		self.schema_ex = {
							'Nesting':[Video, Frame],

							Frame: {
									'image':{
													'mode':'disk',
													'filename':'image.png',
													'load_func':lambda p: imread(p),
													'save_func':lambda x, p: imsave(p, x)
											},
									'subtitles':{
													'mode':'memory'
												}
									},
							Video: {

									'description':{
													'mode':'memory'
												},
									'thumbnail':{
													'mode':'disk',
													'filename':'thumbnail.png',
													'load_func':lambda p: imread(p),
													'save_func':lambda x, p:imsave(p, x)
												}
								}
						}

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
									}
						}
					
		self.image_path = os.path.join(self.root, 'image.png')
		self.image_backup_path = os.path.join(self.root, 'image.backup.png')
		shutil.copy(self.image_backup_path, self.image_path)






	################################################################################
	####################[ ITEM ACCESS TESTS	]#######################################
	################################################################################

	def test_creation(self):
		"""
			BASIC CREATION
			--------------
			merely constructs a DataObject
		"""
		d = DataObject(deepcopy(self.mongo_doc), self.schema_ex[Frame])


	def test_getitem(self):
		"""
			BASIC GETITEM
			-------------
			gets image and subtitles
		"""
		d = DataObject(deepcopy(self.mongo_doc), self.schema_ex[Frame])
		self.assertEqual(d['image'].shape, (512, 512, 3))
		self.assertEqual(d['subtitles'], 'hello, world!')


	def test_setitem(self):
		"""
			BASIC SETITEM TEST
			------------------
			gets image and subtitles
		"""
		d = DataObject(deepcopy(self.mongo_doc), self.schema_ex[Frame])

		img = d['image']
		sub = d['subtitles']

		os.remove(self.image_path)
		d['image'] = img
		d['subtitles'] = 'konnichiwa, sekai!'

		self.assertTrue(os.path.exists(self.image_path))
		self.assertEqual(d['image'].shape, (512, 512, 3))
		self.assertEqual(d['subtitles'], 'konnichiwa, sekai!')


	def test_delitem(self):
		"""
			BASIC DELITEM TEST
			------------------
			removes both, makes sure it works
		"""
		d = DataObject(deepcopy(self.mongo_doc), self.schema_ex[Frame])
		
		del d['image']
		del d['subtitles']

		self.assertTrue(d['image'] is None)
		self.assertTrue(not os.path.exists(self.image_path))
		self.assertTrue(d['subtitles'] is None)


	def test_update_item_metadata(self):
		"""
			BASIC ITEM METADATA UPDATE TEST 
			-------------------------------
			checks on items present, absent, etc.
		"""
		mongo_doc = deepcopy(self.mongo_doc)
		d = DataObject(mongo_doc, self.schema_ex[Frame])

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




