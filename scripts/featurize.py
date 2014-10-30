'''
Script: featurize.py
====================

Description:
------------
	
	For each frame, finds/stores a user-specified feature representation.
	For instructions on how to make Featurizers, see Featurizer.py.

Args:
-----
	
	--featurizer: Import location for featurizer. Ex: MyProject.Featurizers.featurizer1
	--replace: Boolean: replace existing featurized frames?

Usage:
------

	python featurize.py --featurizer Featurizers.featurizer1 --replace


##############
Jay Hack
Fall 2014
jhack@stanford.edu
##############
'''
import click
from ModalDB import *
from schema import FrameSchema


@click.command()
@click.option('--featurizer', help='Import location for featurizer. Ex: MyProject.Featurizers.featurizer1')
@click.option('--replace/--no-replace', help='Boolean: replace existing featurized frames?', default=True)
def Featurize(featurizer, replace):
	"""
		Iterates over all frames in the database and featurizes them 
	"""
	#=====[ Step 1: Get featurizer class	]=====
	click.echo("---> Loading featurizer class")
	splits = featurizer.split('.')
	module_name, class_name = '.'.join(splits[:-1]), splits[-1]
	Featurizer = __import__(module_name, fromlist=[class_name])
	featurizer = Featurizer()

	#=====[ Step 2: Apply it	]=====
	click.echo("---> Featurizing frames")
	db = ModalDB(FrameSchema)
	for frame in db.iter_frames(verbose=True):
		featurizer.featurize(frame)



if __name__ == '__main__':
	Featurize()







