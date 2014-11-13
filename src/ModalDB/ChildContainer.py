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
		childtypes = self.get_childtypes()
		if not len(childtypes) == 1:
			raise Exception("You need to specify the child's datatype")
		return childtypes[0]

	def is_full_id(self, _id):
		return _id.startswith(self.parent_prefix)

	def is_raw_id(self, _id):
		return not self.is_full_id(_id)

	def to_raw_id(self, _id):
		_id = str(_id)
		if self.is_full_id(_id):
			return _id[len(self.parent_prefix):]
		return _id

	def to_full_id(self, _id):
		_id = str(_id)
		if self.is_raw_id(_id):
			return self.parent_prefix + _id
		return _id

	def get_childtype_dict(self, datatype_str):
		return self.childtype_dicts[datatype_str]



	################################################################################
	####################[ GET/ADD	]###############################################
	################################################################################

	def sanitize(self, *args):
		"""
			sanitizes **args; raises exceptions if appropriate;
			returns (childtype, raw_id) 
		"""
		childtypes = self.get_childtypes()

		#=====[ Case: No childtypes: can't get/add children	]=====
		if len(childtypes) == 0:
			raise Exception("No childtypes defined in Schema; operation illegal")

		#=====[ Case: just child_id specified	]=====
		if len(args) == 1:
			if not len(childtypes) == 1:
				raise TypeError("Multiple childtypes exist; need to specify one")
			return (self.get_only_childtype(), self.to_raw_id(args[0]))


		#=====[ Case: datatype, child_id specified	]=====
		elif len(args) == 2:
			if not self.is_valid_childtype(args[0]):
				raise TypeError("Not a valid childtype: %s" % args[0].__name__)
			return (args[0].__name__, self.to_raw_id(args[1]))


		#=====[ Case: invalid # of arguments	]=====
		else:
			raise Exception("Invalid number of arguments")


	def get_full_id(self, *args):
		"""
			Args:
			-----
			- (Optional, first): childtype (can omit if there's only one)
			- raw id of child
		"""
		childtype, raw_id = self.sanitize(*args)		
		childtype_dict = self.get_childtype_dict(childtype)
		return self.get_childtype_dict(childtype)[raw_id]


	def add_child(self, *args):
		"""
			Args:
			-----
			- (Optional, first): childtype (can omit if there's only one)
			- id of child; can be either full or raw
		"""
		childtype, raw_id = self.sanitize(*args)
		full_id = self.to_full_id(raw_id)
		childtype_dict = self.get_childtype_dict(childtype)
		childtype_dict[raw_id] = full_id




