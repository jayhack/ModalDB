'''
Script: configure_mongodb.py
============================

Description:
------------
	
	This script allows one to convert data as it appears in its processed form (after format_data.py)
	to a mongodb database accessible by the StorageDelegate class. This provides a significant speedup 
	and flexible schema for storing data.


Usage: 
------

	python configure_mongodb.py --dbpath [path to data directory] --schema_dict [path to file containing schema]

	i.e.

	python make_mongod_database.py --dbpath ./data --schema_dict schema.Schema


Args:
-----

	--dbpath: path to directory containing data
	--schema_file: import location of python dict containing schema. Ex: myproject.schema

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

from ModalDB import *

@click.command()
@click.option('--dbpath', help='path to directory containing data')
@click.option('--schema_file', help='import location of python dict containing schema. Ex: myproject.schema', default=None)
def configure_mongodb(dbpath, schema_file):
	"""
		Configures/initializes the mongodb database
	"""
	schema = __import__(schema_file).Schema
	client = ModalClient(root=dbpath, schema=schema)

	#=====[ Step 1: Erase old tables	]=====
	click.echo("---> Clearing MongoDB")
	client.clear_db()

	#=====[ Step 2: Add Videos	]=====
	click.echo("---> Adding videos")
	videos_dir = os.path.join(dbpath, 'Video')
	for video_name in [v for v in os.listdir(videos_dir) if not v.startswith('.')]:

		#=====[ Step 2.1: add video (no item_data)	]=====
		click.echo("	---> Adding video: %s" % video_name)
		video_data = {}
		video = client.insert_object(Video, video_name, video_data, parent=None, method='cp')
		
		#=====[ Step 2.2: add Frames as children	]=====
		frames_dir = os.path.join(video.root, 'Frame')
		for frame_name in [d for d in os.listdir(frames_dir) if not d.startswith('.')]:

			frame_data = {
							'image':os.path.join(frames_dir, frame_name, 'image.png'),
							'masks':os.path.join(frames_dir, frame_name, 'masks_and_scores.mat'),
							'scores':os.path.join(frames_dir, frame_name, 'masks_and_scores.mat'),
							'cnn_features':os.path.join(frames_dir, frame_name, 'features.npy')
			}
			client.insert_object(Frame, frame_name, frame_data, parent=video, method='cp')


if __name__ == '__main__':
	configure_mongodb()









