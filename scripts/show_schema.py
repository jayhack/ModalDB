'''
Script: show_schema.py
======================

Description:
------------
	
	Shows the database's current schema


Usage: 
------

	python show_schema.py


##############
Jay Hack
Fall 2014
jhack@stanford.edu
##############
'''
import click
from ModalDB import *

@click.command()
def show_schema():
	db = ModalDB()
	print '==========[ Current Schema ]=========='
	db.print_schema()

if __name__ == '__main__':
	show_schema()
