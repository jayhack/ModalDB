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
from nose.tools import *
from scipy.io import loadmat, savemat
from scipy.misc import imsave, imread
from ModalDB import *

class Test_ModalDBSchema(unittest.TestCase):

	def creation_test_1(self):
		"""
			just creation of basic schema 
		"""
		ModalDBSchema({
						'Nesting':{Video:{Frame}},

						Frame: {
									'image':{
												'mode':'disk',
												'load_func':imread
											},	
									'skeleton':{
												'mode':'disk',
												'load_func':loadmat
									}
								},

						Video: {

									'subtitles':{
												'mode':'memory'
									}
						}
					})


	@raises(TypeError)
	def creation_test_2(self):
		"""
			creation of schema with wrong top-level keys 
		"""
		ModalDBSchema({
						'Nesting':{Video:{Frame}},
						
						'Frame': {
									'image':{
												'mode':'disk',
												'load_func':imread
											},	
									'skeleton':{
												'mode':'disk',
												'load_func':loadmat
									}
								},

						'Video': {

									'subtitles':{
												'mode':'memory'
									}
						}
					})

