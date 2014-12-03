import os
from random import sample
import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt

from RecipeWatchRelated import *

def load_cluster_data(data_dir):
	"""
		returns a dataframe with columns:
			- cluster_id
			- video_id
			- frame_id
			- mask_id
	"""
	return pd.DataFrame({
        'cluster_id': np.load(os.path.join(data_dir, 'cluster_ids.npy')),
        'video_id':np.load(os.path.join(data_dir, 'video_ids.npy')),
        'frame_id':np.load(os.path.join(data_dir, 'frame_ids.npy')),
        'mask_id':np.load(os.path.join(data_dir, 'mask_ids.npy'))
    })


def sample_cluster(df, cluster_id, samples=9):
	"""
		returns a sampled df from the named cluster of size 'samples'
	"""
	cluster_df = df.ix[df['cluster_id'] == cluster_id]
	random_ixs = sample(cluster_df.index, samples)
	return df.ix[random_ixs]


def visualize_cluster_sample(sd, df, cluster_id):
	"""
		plots a sample of object proposals in a given 
		cluster 
	"""
	samples = sample_cluster(df, cluster_id)
	for i in range(9):
		sample_row = samples.iloc[i]
		video = sd.get_video(sample_row['video_id'])
		frame = video.get_frame(sample_row['frame_id'])

		plt.subplot(3, 3, i)
		plt.gca().set_xticks([])
		plt.gca().set_yticks([])
		plt.imshow(frame.visualize_mask(sample_row['mask_id']))

	plt.show()





if __name__ == '__main__':

	sd = StorageDelegate()
	df = load_cluster_data('./data')

	visualize_cluster_sample(sd, df, 1)




