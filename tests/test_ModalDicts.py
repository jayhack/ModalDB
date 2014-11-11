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
import unittest 
import nose
from copy import copy, deepcopy
from nose.tools import *
from scipy.io import loadmat, savemat
from scipy.misc import imsave, imread

from ModalDB import Frame, Video
from ModalDB.ModalDicts import DiskDict

class Test_ModalSchema(unittest.TestCase):

	################################################################################
	####################[ setUp	]###################################################
	################################################################################

	def setUp(self):
		"""
			creates basic schema 
		"""
		self.root = os.path.join(__file__, 'data_ModalDicts')
		self.schema_ex = {
							'Nesting':[Video, Frame],

							Frame: {
										'image':{
													'mode':'disk',
													'filename':'image.png',
													'load_func':lambda p: imread(p),
													'save_func':lambda x, p: imsave(x, p)
												},	
									},
							Video: {

										'subtitles':{
													'mode':'memory'
													}
									}
						}

		self.mongo_doc = {	
						'root':os.path.join(self.root, 'data'),
						'items':{
									'image':{
												'exists':True,
											}
								}
					}






	################################################################################
	####################[ DiskDict	]###############################################
	################################################################################

	def test_creation_diskdict(self):
		"""
			BASIC CREATION TEST
			-------------------
			merely constructs a ModalSchema
		"""
		d = DiskDict(self.mongo_doc, self.schema_ex[Frame])


