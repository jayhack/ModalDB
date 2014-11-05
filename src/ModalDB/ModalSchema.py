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
							'Nesting':{Video:{Frame}},

							#THIS IS A DATA OBJECT
							Frame: {
										#THIS IS AN ITEM
										'image':{
													'mode':'disk',
													'load_func':lambda p: imread(p),
													'save_func':lambda x, p: imsave(x, p)
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

	"""

	#==========[ Hard Constraints 	]==========
	data_modes = ['memory', 'disk', 'dynamic']


	def __init__(self, schema_dict=None, schema_path=None):
		"""
			parses and validates either schema_dict or schema_path
		"""
		if not schema_dict is None and not schema_path is None:
			raise Exception("specify *either* a schema dict or a path to load from ")

		if not schema_dict is None:
			self.schema_dict = self.parse_schema(schema_dict)

		elif not schema_path is None:
			raise NotImplementedError




	################################################################################
	####################[ Saving	]###############################################
	################################################################################

	def load(self, path):
		"""
			loads schema_dict from provided path
		"""
		self.schema_dict = self.parse_schema(pickle.load(open(path)))


	def save(self, path):
		"""
			saves this to path 
		"""
		pickle.dump(self.schema_dict, open(path, 'w'))




	################################################################################
	####################[ Parsing and Validation	]###############################
	################################################################################

	def parse_schema(self, schema_dict):
		"""
			enforces constraints on schema_dict
			Top-level keys need to be 'Nesting' and other DataObjects

			Args:
			-----
			- schema_dict: dictionary containing schema
		"""
		#=====[ Step 1: Check types of top-level keys	]=====
		if not 'Nesting' in schema_dict.keys():
			raise TypeError("You must specify the nesting of DataObjects with top-level key 'Nesting'!")
		if not all([issubclass(key, DataObject) for key in [k for k in schema_dict.keys() if not k == 'Nesting']]):
			raise TypeError("Top-level keys in schema must be subclasses of DataObject or 'Nesting'!")


		#=====[ Step 2: Check individual data objects	]=====
		for obj_name, obj_dict in [(k,v) for k,v in schema_dict.items() if not k == 'Nesting']:
			try:
				schema_dict[obj_name] = self.parse_data_object(obj_dict)
			except TypeError as T:
				print "Error in schema for DataObject: %s" % str(obj_name)
				raise T

		return schema_dict


	def parse_data_object(self, obj_dict):
		"""
			enforces constraints on obj_dicts
			returns them properly formatted
		"""
		#=====[ Step 1: Check types of top-level keys 	]=====
		if not all([type(k)==str and type(v)==dict for k,v in obj_dict.items()]):
			raise Exception("Top-level keys in DataObject schemas must all be strings mapping to dicts!")

		#=====[ Step 2: Check individual item dicts	]=====
		for item_name, item_dict in obj_dict.items():
			try:
				obj_dict[item_name] = self.parse_item(item_name, item_dict)
			except TypeError as T:
				print "Error in schema for item: %s" % item_name
				raise T

		return obj_dict


	def parse_item(self, item_name, item_dict):
		"""
			enforces constraints on item_dicts
			returns them formatted
		"""
		#=====[ Step 1: Deal with 'mode'	]=====
		if 'mode' in item_dict:
			if not item_dict['mode'] in self.data_modes:
				raise TypeError("Entered mode is not valid; valid modes are %s" % self.data_modes)
		else:
			item_dict['mode'] = 'memory'


		#=====[ Step 2: Deal with disk items	]=====
		if item_dict['mode'] == 'disk':

			#=====[ load_func	]=====
			if not 'load_func' in item_dict:
				raise TypeError("All disk items require a load_func")
			else:
				if not inspect.isfunction(item_dict['load_func']):
					raise TypeError("load_func must be an acutal function")
				if not len(inspect.getargspec(item_dict['load_func']).args) == 1:
					raise TypeError("load_func must take only one argument (filepath)")

			#=====[ save_func	]=====
			if not 'save_func'in item_dict:
				item_dict['load_func'] = None
			else:
				if not inspect.isfunction(item_dict['save_func']):
					raise TypeError("save_func must be an acutal function")
				if not len(inspect.getargspec(item_dict['save_func']).args) == 2:
					raise TypeError("save_func must take 2 args (object and filepath)")

			#=====[ filename default: item name	]=====
			if not 'filename' in item_dict:
				item_dict['filename'] = item_name
			if not type(item_dict['filename']) == str:
				raise TypeError("filename must be a string")


		#=====[ Step 3: deal with memory items	]=====
		if item_dict['mode'] == 'memory':
			#####[ TODO: parse memory ]#####
			pass

		#=====[ Step 4: deal with dynamic items	]=====
		if item_dict['mode'] == 'dynamic':
			raise NotImplementedError

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





