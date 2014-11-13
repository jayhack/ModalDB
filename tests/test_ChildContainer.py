"""
Test: ChildContainer
====================

Description:
------------
	
	Tests ChildContainer with mockup mongodb 'children'
	documents.


##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
"""
import unittest 
from copy import copy, deepcopy
import nose
from nose.tools import *

from ModalDB.ChildContainer import ChildContainer

class Test_ChildContainer(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass


	################################################################################
	####################[ GET METHOD	]###########################################
	################################################################################

	@raises(Exception)
	def test_no_children_get(self):
		"""
			ChildContainer: NO CHILDREN GET 
			-------------------------------
			Should throw an exception upon trying to get children
		"""
		mongo_doc = {'children':{}}
		c = ChildContainer('parent_1', mongo_doc)
		c.get_id(Frame, 'child_1')


	def test_single_childtype_get(self):
		"""
			ChildContainer: SINGLE CHILDTYPE GET
			------------------------------------
			Constructs a ChildContainer a single childtype, tests
			get method
		"""
		mongo_doc = {'children':{}}
		mongo_doc['children'] = {'Frame':{'frame_1':'parent_id/frame_1'}}
		c = ChildContainer('parent_id', mongo_doc)

		self.assertEqual(c.get_full_id('frame_1'), 'parent_id/frame_1')
		self.assertEqual(c.get_full_id(Frame, 'frame_1'), 'parent_id/frame_1')


	def test_multiple_childtype_get(self):
		"""
			ChildContainer: MULTIPLE CHILDTYPE GET
			---------------------------------------
			Constructs a ChildContainer w/ multiple childtypes, tests
			get method
		"""
		mongo_doc = {'children':{}}
		mongo_doc['children']['Frame'] = {'frame_1':'parent_id/frame_1'}
		mongo_doc['children']['Video'] = {'video_1':'parent_id/video_1'}
		c = ChildContainer('parent_id', mongo_doc)

		self.assertEqual(c.get_full_id(Frame, 'frame_1'), 'parent_id/frame_1')
		self.assertEqual(c.get_full_id(Video, 'video_1'), 'parent_id/video_1')		


	@raises(TypeError)
	def test_access_bad_childtype(self):
		"""
			ChildContainer: ACCESS WITH BAD CHILDTYPE 
			-----------------------------------------
			Tries to get_child with a bad childtype
		"""
		mongo_doc = {'children':{}}
		mongo_doc['children'] = {'Frame':{'frame_1':'parent_id/frame_1'}}
		c = ChildContainer('parent_1', mongo_doc)
		c.get_full_id(Video, 'frame_1')


	@raises(TypeError)
	def test_access_bad_child_id(self):
		"""
			ChildContainer: ACCESS WITH BAD CHILD_ID
			----------------------------------------
			Tries to get_child with a bad childtype
		"""
		mongo_doc = {'children':{}}
		mongo_doc['children'] = {'Frame':{'frame_1':'parent_id/frame_1'}}
		c = ChildContainer('parent_1', mongo_doc)
		c.get_full_id(Frame, 'frame_2')







	################################################################################
	####################[ ADD METHOD	]###########################################
	################################################################################

	@raises(Exception)
	def test_no_children_add(self):
		"""
			ChildContainer: NO CHILDREN ADD 
			-------------------------------
			Should throw an exception upon trying to get children
		"""
		mongo_doc = {'children':{}}
		c = ChildContainer('parent_1', mongo_doc)
		c.add_child(Frame, 'child_1')


	def test_single_childtype_add(self):
		"""
			ChildContainer: SINGLE CHILDTYPE ADD 
			------------------------------------
			Constructs a ChildContainer with a single childtype, tests 
			add method
		"""
		mongo_doc = {'children':{}}
		mongo_doc['children'] = {'Frame':{'frame_1':'parent_id/frame_1'}}
		c = ChildContainer('parent_id', mongo_doc)

		c.add_child('frame_2')
		c.add_child(Frame, 'frame_3')

		self.assertEqual(c.get_full_id('frame_2'), 'parent_id/frame_2')
		self.assertEqual(c.get_full_id(Frame, 'frame_2'), 'parent_id/frame_2')		

		self.assertEqual(c.get_full_id('frame_3'), 'parent_id/frame_3')
		self.assertEqual(c.get_full_id(Frame, 'frame_2'), 'parent_id/frame_3')	


	def test_multiple_childtype_add(self):
		"""
			ChildContainer: MULTIPLE_CHILDTYPE_ADD 
			--------------------------------------
			Constructs a ChildContainer with multiple childtypes, tests
			add method
		"""
		mongo_doc = {'children':{}}
		mongo_doc['children']['Frame'] = {'frame_1':'parent_id/frame_1'}
		mongo_doc['children']['Video'] = {'video_1':'parent_id/video_1'}
		c = ChildContainer('parent_id', mongo_doc)

		c.add_child(Frame, 'frame_2')
		c.add_child(Video, 'video_2')

		self.assertEqual(c.get_full_id(Frame, 'frame_2'), 'parent_id/frame_2')
		self.assertEqual(c.get_full_id(Video, 'video_2'), 'parent_id/video_2')	








