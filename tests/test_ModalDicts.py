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
from copy import copy, deepcopy
import unittest
import nose
from nose.tools import *
from scipy.io import loadmat, savemat
from scipy.misc import imsave, imread

from ModalDB import Frame, Video
from ModalDB.ModalDicts import DiskDict, MemoryDict

from schema_example import schema_ex
from dataobject_example import video_data, frame_data

class Test_ModalSchema(unittest.TestCase):

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
		self.schema_ex = schema_ex
		self.mongo_doc = {
							'_id': 'test_video',
							'children': {'Frame': []},
 							'items': {
 										'image':{'present': True},
										'subtitles':{
														'present': True,
														'data':'hello, world!'
													}
									},
							'root':self.root
						}





	################################################################################
	####################[ DiskDict	]###############################################
	################################################################################

	def test_creation_diskdict(self):
		"""
			BASIC DISKDICT CREATION TEST
			----------------------------
			merely constructs a ModalSchema
		"""
		d = DiskDict(deepcopy(self.mongo_doc), self.schema_ex[Frame])


	def test_getitem_diskdict(self):
		"""
			BASIC DISKDICT GETITEM TEST
			---------------------------
			gets the image and confirms that it loaded correctly
		"""
		self.reset_image()
		d = DiskDict(deepcopy(self.mongo_doc), self.schema_ex[Frame])
		img = d['image']
		self.assertEqual(img.shape, (512, 512, 3))


	def test_setitem_diskdict(self):
		"""
			BASIC DISKDICT SETITEM TEST
			---------------------------
			gets the image, deletes it from disk, then saves it 
			and confirms that it saved correctly
		"""
		self.reset_image()
		d = DiskDict(deepcopy(self.mongo_doc), self.schema_ex[Frame])
		img = d['image']
		self.remove_image()
		d['image'] = img
		self.assertTrue(self.image_exists())


	def test_delitem_diskdict(self):
		"""
			BASIC DISKDICT DELITEM TEST
			---------------------------
			removes image, then replaces it 
		"""
		self.reset_image()
		d = DiskDict(deepcopy(self.mongo_doc), self.schema_ex[Frame])
		img = d['image']

		del d['image']
		self.assertTrue(not self.image_exists())
		self.assertEqual(d['image'], None)









	################################################################################
	####################[ MemoryDict	]###########################################
	################################################################################

	def test_creation_memdict(self):
		"""
			BASIC MEMORY DICT CREATION TEST
			-------------------------------
			merely constructs a MemoryDict
		"""
		d = MemoryDict(deepcopy(self.mongo_doc), self.schema_ex[Frame])


	def test_getitem_memdict(self):
		"""
			BASIC MEMORY DICT GETITEM TEST
			------------------------------
			gets subtitles and tests length
		"""
		d = MemoryDict(deepcopy(self.mongo_doc), self.schema_ex[Frame])
		self.assertEqual(d['subtitles'], 'hello, world!')


	def test_setitem_memdict(self):
		"""
			BASIC MEMORY DICT SETITEM TEST
			------------------------------
			sets subtitles to something new
		"""
		d = MemoryDict(deepcopy(self.mongo_doc), self.schema_ex[Frame])
		d['subtitles'] = "konnichiwa, sekai!"
		self.assertEqual(d['subtitles'], "konnichiwa, sekai!")


	def test_delitem_memdict(self):
		"""
			BASIC MEMORY DICT DELITEM TEST
			------------------------------
			removes subtitles, asserts they are actually gone
		"""
		d = MemoryDict(deepcopy(self.mongo_doc), self.schema_ex[Frame])
		del d['subtitles']
		self.assertEquals(d['subtitles'], None)
