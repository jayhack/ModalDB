from ModalDB import *

schema_ex = {
				Frame: {
							'image':{
										'mode':'disk',
										'filename':'image.png',
										'load_func':lambda p: imread(p),
										'save_func':lambda x, p: imsave(p, x)
									},
							'subtitles':{
										'mode':'memory'
										},

						},
				Video: {

							'summary':{
										'mode':'memory'
									},
							'thumbnail':{
										'mode':'disk',
										'filename':'thumbnail.png',
										'load_func':lambda p: imread(p),
										'save_func':lambda x, p: imsave(p, x)
									},
							'contains':[Frame]
						}
			}