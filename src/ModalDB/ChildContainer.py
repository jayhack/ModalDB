'''
Class: ChildContainer
=====================

Description:
------------
	
	Facilitates interaction with a DataObject's children.
	Wraps around a document stored in MongoDB containing children.


Terminology:
------------
raw_id: _id of child in isolation, i.e. 'frame_1'
full_id: _id of child given its parent, i.e. 'video_1/frame_1'


##################
Jay Hack
Fall 2014
jhack@stanford.edu
##################
'''
class ChildContainer(object):
	"""
		Class: ChildContainer
		=====================

		Description:
		------------
			
			Facilitates interaction with a DataObject's children.
			Wraps around a document stored in MongoDB containing children.


		Terminology:
		------------
		raw_id: _id of child in isolation, i.e. 'frame_1'
		full_id: _id of child given its parent, i.e. 'video_1/frame_1'
	"""
	id_joiner = '/'

	def __init__(self, parent_id, mongo_doc):
		""""
			mongo_doc: document containing a DataObject
		"""
		self.parent_id = parent_id
		self.parent_prefix = parent_id + self.id_joiner
		self.childtype_dicts = mongo_doc['children']




	################################################################################
	####################[ UTILS	]###################################################
	################################################################################

	def get_childtypes(self):
		return self.childtype_dicts.keys()

	def no_childtypes(self):
		return len(self.get_childtypes()) == 0

	def is_valid_childtype(self, datatype):
		return datatype.__name__ in self.get_childtypes()

	def get_only_childtype(self):
		if not len(self.get_childtypes) == 1:
			raise Exception("You need to specify the child's datatype")
		return self.get_childtypes()[0]

	def is_full_id(self, _id):
		return _id.startswith(self.parent_prefix)

	def is_raw_id(self, _id):
		return not self.is_full(_id)

	def to_raw_id(self, _id):
		_id = str(_id)
		if self.is_raw_id(_id):
			return _id[len(self.parent_prefix):]
		return _id

	def to_full_id(self, _id):
		_id = str(_id)
		if self.is_full_id(_id):
			return self.parent_prefix + _id
		return _id

	def get_childtype_dict(self, datatype):
		assert self.is_valid_childtype(datatype)
		return self.childtype_dicts[datatype.__name__]



	################################################################################
	####################[ GET/ADD	]###############################################
	################################################################################

	def sanitize(self, func):
		"""
			Wraps get/add_child functions; Calls them with two arguments:
			- childtype: (valid) type of the child
			- raw_id: raw id of the child, i.e. 'frame_1' not 'video_1/frame_1'
		"""
		def func_wrapper(**args):
			childtypes = self.get_childtypes()

			#=====[ Case: No childtypes: can't get/add children	]=====
			if len(childtypes) == 0:
				raise Exception("No childtypes defined in Schema; operation illegal")

			#=====[ Case: just child_id specified	]=====
			if len(args) == 1:
				if not len(childtypes) == 1:
					raise TypeError("Multiple childtypes exist; need to specify one")
				return func(self.get_only_datatype(), args)

			#=====[ Case: datatype, child_id specified	]=====
			elif len(args) == 2:
				if not self.is_valid_childtype(args[0]):
					raise TypeError("Not a valid childtype: %s" % args[0].__name__)
				return func(args[0], self.to_raw_id(args[1]))

			#=====[ Case: invalid # of arguments	]=====
			else:
				raise Exception("Invalid number of arguments")

		return func_wrapper


	@self.sanitize
	def get_full_id(self, childtype, raw_id):
		"""
			Args:
			-----
			- (Optional, first): childtype (can omit if there's only one)
			- raw id of child
		"""
		return self.get_childtype_dict(childtype)[raw_id]


	@sanitize
	def add_child(self, childtype, raw_id):
		"""
			Args:
			-----
			- (Optional, first): childtype (can omit if there's only one)
			- id of child; can be either full or raw
		"""
		full_id = self.to_full_id(raw_id)
		childtype_dict = self.get_childtype_dict(childtype)
		childtype_dict[raw_id] = full_id




