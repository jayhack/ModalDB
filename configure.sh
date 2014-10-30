export PROJECT_DIR=`pwd`
export DATA_DIR=`pwd`/data
export MONGODB_DBPATH=`pwd`/data/db
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/src/

#===[ Add Caffe to Path ]===
export CAFFE_ROOT_DIR=/Users/jayhack/CS/CV/caffe
export PYTHONPATH=$PYTHONPATH:$CAFFE_ROOT_DIR/python

#===[ Add DYLD_FALLBACK_LIBRARY_PATH So Caffe can find .dyld libraries ]===
export DYLD_FALLBACK_LIBRARY_PATH=/usr/local/cuda/lib:/usr/local/Cellar/hdf5/1.8.13/lib/:/usr/local/cuda/lib:/usr/local/Cellar/hdf5/1.8.13/lib/:/usr/local/cuda/lib:/Users/jayhack/anaconda/lib:/usr/local/lib:/usr/lib

#===[ Configure DB ]===
python scripts/configure_mongodb.py --dbpath $DATA_DIR --schema_dict schema.Schema
