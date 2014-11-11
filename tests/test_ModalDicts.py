'''
Test: ModalDicts
================

Description:
------------
	
	Contains funcitonality for working with items of different 
	modalities, one for each.


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

from ModalDB import Frame, Video
from ModalDB.ModalDicts import DiskDict, MemoryDict

class Test_ModalSchema(unittest.TestCase):

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

										'subtitles':{
													'mode':'memory'
													}
									}
						}

		self.mongo_dict = {	
						'root':self.root,
						'items':{
									'image':{
												'exists':True,
											},
									'subtitles':{
												'exists':True,
												'data':'hello, world!'
									}
								}
					}
		self.image_path = os.path.join(self.root, 'image.png')
		self.image_backup_path = os.path.join(self.root, 'image.backup.png')
		shutil.copy(self.image_backup_path, self.image_path)






	################################################################################
	####################[ DiskDict	]###############################################
	################################################################################

	def test_creation_diskdict(self):
		"""
			BASIC DISKDICT CREATION TEST
			----------------------------
			merely constructs a ModalSchema
		"""
		d = DiskDict(deepcopy(self.mongo_dict), self.schema_ex[Frame])


	def test_getitem_diskdict(self):
		"""
			BASIC DISKDICT GETITEM TEST
			---------------------------
			gets the image and confirms that it loaded correctly
		"""
		d = DiskDict(deepcopy(self.mongo_dict), self.schema_ex[Frame])
		img = d['image']
		self.assertEqual(img.shape, (512, 512, 3))


	def test_setitem_diskdict(self):
		"""
			BASIC DISKDICT SETITEM TEST
			---------------------------
			gets the image, deletes it from disk, then saves it 
			and confirms that it saved correctly
		"""
		d = DiskDict(deepcopy(self.mongo_dict), self.schema_ex[Frame])
		img = d['image']
		os.remove(self.image_path)
		d['image'] = img
		self.assertTrue(os.path.exists(self.image_path))


	def test_delitem_diskdict(self):
		"""
			BASIC DISKDICT DELITEM TEST
			---------------------------
			removes image, then replaces it 
		"""
		d = DiskDict(deepcopy(self.mongo_dict), self.schema_ex[Frame])
		img = d['image']

		del d['image']
		self.assertTrue(not os.path.exists(self.image_path))
		self.assertEqual(d['image'], None)
		shutil.copy(self.image_backup_path, self.image_path)









	################################################################################
	####################[ MemoryDict	]###########################################
	################################################################################

	def test_creation_memdict(self):
		"""
			BASIC MEMORY DICT CREATION TEST
			-------------------------------
			merely constructs a MemoryDict
		"""
		d = MemoryDict(deepcopy(self.mongo_dict), self.schema_ex[Frame])


	def test_getitem_memdict(self):
		"""
			BASIC MEMORY DICT GETITEM TEST
			------------------------------
			gets subtitles and tests length
		"""
		d = MemoryDict(deepcopy(self.mongo_dict), self.schema_ex[Frame])
		self.assertEqual(d['subtitles'], 'hello, world!')


	def test_setitem_memdict(self):
		"""
			BASIC MEMORY DICT SETITEM TEST
			------------------------------
			sets subtitles to something new
		"""
		d = MemoryDict(deepcopy(self.mongo_dict), self.schema_ex[Frame])
		d['subtitles'] = "konnichiwa, sekai!"
		self.assertEqual(d['subtitles'], "konnichiwa, sekai!")


	def test_delitem_memdict(self):
		"""
			BASIC MEMORY DICT DELITEM TEST
			------------------------------
			removes subtitles, asserts they are actually gone
		"""
		d = MemoryDict(deepcopy(self.mongo_dict), self.schema_ex[Frame])
		del d['subtitles']
		self.assertEquals(d['subtitles'], None)
