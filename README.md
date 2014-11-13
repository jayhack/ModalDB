ModalDB
=======
Jay Hack (jhack@stanford.edu), Fall 2014

# Overview

ModalDB is a database that allows one to efficiently access and manipulate data heirarchical datasets that contain multiple modalities of Data. It is built on top of MongoDB and was originally developed for the Stanford AI Lab's Robobrain Project. Key features include:

- Ability to store different types of data (e.g. images, videos, text) in different ways (in-memory, on-disk), while providing a seamless interface that hides this fact from the user. For example:

```
In [1]: video_frame['subtitles'] # loads quickly from in-memory
...
In [2]: video_frame['image'] # loads lazily from disk
```

- Ability to define arbitrary nesting hierarchies of Data Objects. For example, 'Videos' can have associated properties (summaries, thumbnails, etc) while also maintaining a collection of 'Frames' internally. In code:

```
In [1]: video['thumbnail'] # loads lazily from disk
...
In [2]: frame = video.get_random_child(Frame)
In [3]: frame['image'] #loads lazily from disk
```


# Setup:
```
	~$: cd ModalDB
	~$: source ./configure.sh
	~$: mongodb --dbpath=$MONGODB_DBPATH
	~$: ipython
	In [1]: from ModalDB import *
	...
```

