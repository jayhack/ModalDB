'''
Script: make_mongodb_database.py
================================

Description:
------------
	
	This script allows one to convert data as it appears in its processed form (after format_data.py)
	to a mongodb database accessible by the StorageDelegate class. This provides a significant speedup 
	and flexible schema for storing data.


Usage: 
------

	python make_mongodb_database.py -i [input_directory]

	i.e.

	python make_mongod_database.py 	-i ./data


Args:
-----

	-i (--input_dir): path to source data directory on local filesystem


##############
Jay Hack
Fall 2014
jhack@stanford.edu
##############
'''
import click
import os
import shutil
import sys
import argparse
from pprint import pprint
from scipy.io import loadmat
import numpy as np
from pymongo import MongoClient

@click.option('--db_path', help='path to directory containing data')
@click.option('--schema_dict', help='import location of python dict containing schema. Ex: schema.FrameSchema')
def make_mongodb_database(dbpath, schema):
	"""
		initializes the mongodb database
	"""
	#=====[ Step 1: Erase old tables	]=====
	click.echo("---> Resetting MongoDB")
	client = MongoClient()
	for db_name in client.database_names():
		if not db_name in ['admin', 'local']:
			client.drop_database(db_name)
	db = client.ModaliDB


	#=====[ Step 2: Add Schema	]=====
	click.echo("---> Setting DB schema")
	splits = schema_dict.split('.')
	module_name, dict_name = '.'.join(splits[:-1]), splits[-1]
	schema_dict = __import__(module_name, fromlist=[dict_name])
	db.schema = schema_dict





if __name__ == '__main__':

	pass
	# #=====[ Insert Videos ]===
	# for video_name in [v for v in os.listdir(input_dir) if not v.startswith('.')]:
	# 	video = {'name':video_name, '_id':video_name}
	# 	video['root_dir'] = os.path.join(input_dir, video_name)
	# 	video['frames_dir'] = os.path.join(input_dir, video_name, 'frames')
	# 	video['frames'] = []
	# 	for frame_name in sorted(os.listdir(video['frames_dir'])):
	# 		frame_dir = os.path.join(video['frames_dir'], frame_name)
	# 		image_path = os.path.join(frame_dir, 'image.jpg')
	# 		masks_and_scores_path = os.path.join(frame_dir, 'masks_and_scores.mat')
	# 		if not os.path.exists(masks_and_scores_path):
	# 			masks_and_scores_path = None
	# 		frame = {'root_dir':frame_dir, 'image_path':image_path, 'masks_and_scores_path':masks_and_scores_path, 'name':frame_name, '_id':frame_name}
	# 		video['frames'].append(frame)
	# 	print '---> Inserting video: %s' % video_name

	# 	db.videos.insert(video)









