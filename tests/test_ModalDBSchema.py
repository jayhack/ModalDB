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

	def test_creation_1(self):
		"""
			BASIC CREATION TEST
			-------------------
			merely constructs a ModalDBSchema
		"""
		ModalDBSchema({
						'Nesting':{Video:{Frame}},

						Frame: {
									'image':{
												'mode':'disk',
												'load_func':lambda p: imread(p)
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


	@raises(TypeError)
	def test_creation_2(self):
		"""
			NEGATIVE TEST
			-------------
			should raise a TypeError due to top-level keys being 
			strings
		"""
		ModalDBSchema({
						'Nesting':{Video:{Frame}},
						
						'Frame': {
									'image':{
												'mode':'disk',
												'load_func':lambda p: imread(x),
											},	
									'skeleton':{
												'mode':'disk',
												'load_func':lambda p: loadmat(p),
									}
								},

						'Video': {

									'subtitles':{
												'mode':'memory'
									}
						}
					})


	@raises(TypeError)
	def creation_test_3(self):
		"""
			NEGATIVE TEST
			-------------
			should raise a TypeError due to disk-items not specifying 
			load functions
		"""
		ModalDBSchema({
						'Nesting':{Video:{Frame}},
						
						Frame: {
									'image':{
												'mode':'disk',
											},	
									'skeleton':{
												'mode':'disk',
									}
								},

						Video: {

									'subtitles':{
												'mode':'memory'
									}
						}
					})

