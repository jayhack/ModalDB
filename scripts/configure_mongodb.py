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
	--schema_dict: import location of python dict containing schema. Ex: schema.Schema

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

@click.command()
@click.option('--dbpath', help='path to directory containing data')
@click.option('--schema_dict', help='import location of python dict containing schema. Ex: schema.Schema')
def configure_mongodb(dbpath, schema_dict):
	"""
		Configures/initializes the mongob database
	"""
	#=====[ Step 1: Erase old tables	]=====
	click.echo("---> Resetting MongoDB")
	client = MongoClient()
	for db_name in client.database_names():
		if not db_name in ['admin', 'local']:
			client.drop_database(db_name)
	db = client.ModalDB


	#=====[ Step 2: Set schema	]=====
	click.echo("---> Setting DB schema")
	splits = schema_dict.split('.')
	module_name, dict_name = '.'.join(splits[:-1]), splits[-1]
	schema_dict = __import__(module_name, fromlist=[dict_name])
	db.schema = schema_dict


	#=====[ Step 3: Add Videos	]=====
	click.echo("---> Adding videos")
	videos_dir = os.path.join(dbpath, 'videos')
	for video_name in [v for v in os.listdir(videos_dir) if not v.startswith('.')]:
		video = {'name':video_name, '_id':video_name}
		video['root_dir'] = os.path.join(videos_dir, video_name)
		video['frames_dir'] = os.path.join(videos_dir, video_name, 'frames')

		video['frames'] = {}
		for frame_name in sorted(os.listdir(video['frames_dir'])):
			frame_dir = os.path.join(video['frames_dir'], frame_name)
			frame = {'_id':frame_name, 'root_dir':frame_dir}
			video['frames'][frame_name] = frame
		click.echo('	---> Inserting video: %s' % video_name)
		db.videos.insert(video)


if __name__ == '__main__':
	configure_mongodb()









