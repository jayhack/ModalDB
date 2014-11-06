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
	client = ModalClient(root=dbpath)

	#=====[ Step 1: Erase old tables	]=====
	click.echo("---> Clearing MongoDB")
	client.clear_db()

	#=====[ Step 2: Add Videos	]=====
	click.echo("---> Adding videos")
	videos_dir = os.path.join(dbpath, 'Video')
	for video_name in [v for v in os.listdir(videos_dir) if not v.startswith('.')]:

		#=====[ Step 2.1: add video	]=====
		client.insert_object(Video, None, video_name)
		
		# frames_dir = os.path.join(video.root, 'Frame')
		# for frame_dir in [d for d in os.listdir(frames_dir) if not d.startswith('.')]:
		# 	client.insert_object()

		#=====[ Step 2.2: add children to video	]=====
		# video_dir = os.path.join(videos_dir, video_name)
		# frames_dir = os.path.join(video_dir, 'Frame')
		


		# frame_dirs = [d for d in os.listdir(video_dir) if not d.startswith('.')]
		# for frame_dir in frame_dirs:
		# 	video = client.get_object(Video, video_name)
		# 	video.insert_child()

		# video['frames'] = {}
		# for frame_name in sorted(os.listdir(video['frames_dir'])):
		# 	frame_dir = os.path.join(video['frames_dir'], frame_name)
		# 	frame = {'_id':frame_name, 'root_dir':frame_dir}
		# 	video['frames'][frame_name] = frame
		# click.echo('	---> Inserting video: %s' % video_name)
		# db.videos.insert(video)


if __name__ == '__main__':
	configure_mongodb()









