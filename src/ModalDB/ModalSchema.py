'''
Class: ModalSchema
==================

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
import inspect
import dill as pickle
from pprint import pformat

from DataObject import *

class ModalSchema(object):
	"""
		Class: ModalSchema
		==================

		Contains functionality for dealing with and interpreting ModalDB 
		schemas.


		Example Usage:
		--------------

		ModalSchema({
						Frame: {
									'image':{
												'mode':'disk',
												'filename':'image.png',
												'load_func':lambda p: imread(p),
												'save_func':lambda x, p: imsave(p, x)
											},
									'subs':{
												'mode':'memory'
											}
								},
						Video: {

									'summary':{
												'mode':'memory'
											},
									'thumbnail':{
												'mode':'disk',
												'filename':'thumbnail.png',
												'load_func':lambda p: imread(p),
												'save_func':lambda x, p: imsave(p, x)
											},
									'contains':[Frame]
								}
					})

	"""

	#==========[ Hard Constraints 	]==========
	data_modes = ['memory', 'disk']


	def __init__(self, schema_path_or_dict=None):
		"""
			parses and validates either schema_dict or schema_path
		"""
		if type(schema_path_or_dict) == dict:
			self.schema_dict = self.parse_schema(schema_path_or_dict)

		elif type(schema_path_or_dict) in [str, unicode]:
			self.load(schema_path_or_dict)

		else:
			raise Exception("Schema must be initialized with a dict or a path")




	################################################################################
	####################[ LOADING/SAVING	]#######################################
	################################################################################

	def load(self, path):
		self.schema_dict = self.parse_schema(pickle.load(open(path)))

	def save(self, path):
		pickle.dump(self.schema_dict, open(path, 'w'))



	################################################################################
	####################[ GETTING ITEMS	]###########################################
	################################################################################

	def __getitem__(self, key):
		return self.schema_dict[key]

	def keys(self):
		return self.schema_dict.keys()

		


	################################################################################
	####################[ PARSING/VALIDATION	]###################################
	################################################################################

	def parse_schema(self, schema_dict):
		"""
			enforces constraints on schema_dict:
			- Top-level keys must be DataObject subclasses
			- 'contains' must be a list of DataObject subclasses
			returns it properly formatted
		"""
		#=====[ Step 1: Check types of top-level keys	]=====
		if not all([issubclass(key, DataObject) for key in schema_dict.keys()]):
			raise TypeError

		#=====[ Step 2: Check individual data objects	]=====
		for obj_name, obj_dict in schema_dict.items():
			schema_dict[obj_name] = self.parse_data_object(obj_dict)

		return schema_dict


	def parse_data_object(self, obj_dict):
		"""
			enforces constraints on obj_dict:
			- Top-level keys must be strings
			- 'contains' maps to a list of DataObject subclasses
			- all items map to dicts
		"""
		#=====[ Step 1: 'contains' formatting	]=====
		if 'contains' in obj_dict.keys():
			if not type(obj_dict['contains']) == list:
				raise TypeError
			if not all(issubclass(x, DataObject) for x in obj_dict['contains']):
				raise TypeError("'contains' must consist of DataObject subclasses")
		else:
			obj_dict['contains'] = []

		#=====[ Step 2: items formatting	]=====
		if not all([type(k) == str for k in obj_dict.keys()]):
			raise TypeError
		if not all([type(v) == dict for k,v in obj_dict.items() if not k == 'contains']):
			raise TypeError

		#=====[ Step 3: parse item dicts	]=====
		for item_name, item_dict in [(k,v) for k,v in obj_dict.items() if not k == 'contains']:
			obj_dict[item_name] = self.parse_item(item_name, item_dict)

		return obj_dict


	def parse_item(self, item_name, item_dict):
		"""
			enforces constraints on item_dicts
			returns them formatted
		"""
		#=====[ Step 1: Deal with 'mode'	]=====
		if not 'mode' in item_dict:
			item_dict['mode'] = 'memory'
		if not item_dict['mode'] in self.data_modes:
			raise TypeError


		#=====[ Step 2: Deal with disk items	]=====
		if item_dict['mode'] == 'disk':

			#=====[ load_func	]=====
			if not 'load_func' in item_dict:
				raise TypeError
			if not inspect.isfunction(item_dict['load_func']):
				raise TypeError
			if not len(inspect.getargspec(item_dict['load_func']).args) == 1:
				raise TypeError

			#=====[ save_func	]=====
			if not 'save_func' in item_dict or item_dict['save_func'] is None:
				item_dict['save_func'] = None
			else:
				if not inspect.isfunction(item_dict['save_func']):
					raise TypeError
				if not len(inspect.getargspec(item_dict['save_func']).args) == 2:
					raise TypeError

			#=====[ filename	]=====
			if not 'filename' in item_dict:
				item_dict['filename'] = item_name
			if not type(item_dict['filename']) in [str, unicode]:
				raise TypeError


		#=====[ Step 3: deal with memory items	]=====
		if item_dict['mode'] == 'memory':
			pass

		return item_dict





	################################################################################
	####################[ Adding Items	]###########################################
	################################################################################

	def add_data_object(self, object_type, object_dict):
		"""
			adds an item to specified data_object 
		"""
		object_dict = self.parse_data_object(object_dict)
		self.schema_dict[object_type] = object_dict


	def add_item(self, data_object, item_name, item_dict):
		"""
			adds an item to specified data_object 
		"""
		item_dict = self.parse_item(item_name, item_dict)
		self.schema_dict[data_object][item_name] = item_dict



