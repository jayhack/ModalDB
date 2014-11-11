from ModalDB import *
import os

data_dir = os.path.join(os.path.split(__file__)[0], 'data_ModalClient')

video_data = {
				'summary':'hello, world!',
				'thumbnail':os.path.join(data_dir, 'thumbnail.png')
			}

frame_data = {
				'subtitles':'hello, world!',
				'image':os.path.join(data_dir, 'image.png')
			}