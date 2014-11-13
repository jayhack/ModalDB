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

from ModalDB import *
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
		schema = {'contains':[]}
		mongo_doc = {'children':{}}

		c = ChildContainer('parent_1', schema, mongo_doc)

		c.get(Frame, 'child_1')


	def test_single_childtype_get(self):
		"""
			ChildContainer: SINGLE CHILDTYPE GET
			------------------------------------
			Constructs a ChildContainer a single childtype, tests
			get method
		"""
		schema = {'contains':[Frame]}
		mongo_doc = {'children':{}}
		mongo_doc['children'] = {'Frame':{'frame_1':'parent_id/frame_1'}}

		c = ChildContainer('parent_id', schema, mongo_doc)

		self.assertEqual(c.get('frame_1')[0], Frame)
		self.assertEqual(c.get('frame_1')[1], 'parent_id/frame_1')		
		self.assertEqual(c.get(Frame, 'frame_1')[1], 'parent_id/frame_1')


	def test_multiple_childtype_get(self):
		"""
			ChildContainer: MULTIPLE CHILDTYPE GET
			---------------------------------------
			Constructs a ChildContainer w/ multiple childtypes, tests
			get method
		"""
		schema = {'contains':[Video, Frame]}
		mongo_doc = {'children':{}}
		mongo_doc['children']['Frame'] = {'frame_1':'parent_id/frame_1'}
		mongo_doc['children']['Video'] = {'video_1':'parent_id/video_1'}

		c = ChildContainer('parent_id', schema, mongo_doc)

		self.assertEqual(c.get(Frame, 'frame_1')[0], Frame)
		self.assertEqual(c.get(Frame, 'frame_1')[1], 'parent_id/frame_1')		
		self.assertEqual(c.get(Video, 'video_1')[0], Video)
		self.assertEqual(c.get(Video, 'video_1')[1], 'parent_id/video_1')		



	@raises(TypeError)
	def test_access_bad_childtype(self):
		"""
			ChildContainer: ACCESS WITH BAD CHILDTYPE 
			-----------------------------------------
			Tries to get_child with a bad childtype
		"""
		schema = {'contains':[Frame]}
		mongo_doc = {'children':{}}
		mongo_doc['children'] = {'Frame':{'frame_1':'parent_id/frame_1'}}
		c = ChildContainer('parent_1', schema, mongo_doc)
		c.get(Video, 'frame_1')


	@raises(KeyError)
	def test_access_bad_child_id(self):
		"""
			ChildContainer: ACCESS WITH BAD CHILD_ID
			----------------------------------------
			Tries to get_child with a bad childtype
		"""
		schema = {'contains':[Frame]}
		mongo_doc = {'children':{}}
		mongo_doc['children'] = {'Frame':{'frame_1':'parent_id/frame_1'}}
		c = ChildContainer('parent_1', schema, mongo_doc)
		c.get(Frame, 'frame_2')







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
		schema = {'contains':[]}
		mongo_doc = {'children':{}}
		c = ChildContainer('parent_1', mongo_doc)
		c.add(Frame, 'child_1')


	def test_single_childtype_add(self):
		"""
			ChildContainer: SINGLE CHILDTYPE ADD 
			------------------------------------
			Constructs a ChildContainer with a single childtype, tests 
			add method
		"""
		schema = {'contains':[Frame]}
		mongo_doc = {'children':{}}
		mongo_doc['children'] = {'Frame':{'frame_1':'parent_id/frame_1'}}
		c = ChildContainer('parent_id', schema, mongo_doc)

		c.add('frame_2')
		c.add(Frame, 'frame_3')

		self.assertEqual(c.get('frame_2')[0], Frame)
		self.assertEqual(c.get('frame_2')[1], 'parent_id/frame_2')
		self.assertEqual(c.get(Frame, 'frame_2')[0], Frame)
		self.assertEqual(c.get(Frame, 'frame_2')[1], 'parent_id/frame_2')

		self.assertEqual(c.get('frame_3')[0], Frame)
		self.assertEqual(c.get('frame_3')[1], 'parent_id/frame_3')
		self.assertEqual(c.get(Frame, 'frame_3')[0], Frame)
		self.assertEqual(c.get(Frame, 'frame_3')[1], 'parent_id/frame_3')


	def test_multiple_childtype_add(self):
		"""
			ChildContainer: MULTIPLE_CHILDTYPE_ADD 
			--------------------------------------
			Constructs a ChildContainer with multiple childtypes, tests
			add method
		"""
		schema = {'contains':[Frame, Video]}
		mongo_doc = {'children':{}}
		mongo_doc['children']['Frame'] = {'frame_1':'parent_id/frame_1'}
		mongo_doc['children']['Video'] = {'video_1':'parent_id/video_1'}
		c = ChildContainer('parent_id', schema, mongo_doc)

		c.add(Frame, 'frame_2')
		c.add(Video, 'video_2')

		self.assertEqual(c.get(Frame, 'frame_2')[0], Frame)
		self.assertEqual(c.get(Frame, 'frame_2')[1], 'parent_id/frame_2')		
		self.assertEqual(c.get(Video, 'video_2')[0], Video)
		self.assertEqual(c.get(Video, 'video_2')[1], 'parent_id/video_2')








