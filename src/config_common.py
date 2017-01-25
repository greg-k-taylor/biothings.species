
#############
# HUB VARS  #
#############

DATA_SRC_MASTER_COLLECTION = 'src_master'   # for metadata of each src collections
DATA_SRC_DUMP_COLLECTION = 'src_dump'       # for src data download information
DATA_SRC_BUILD_COLLECTION = 'src_build'     # for src data build information

DATA_TARGET_MASTER_COLLECTION = 'db_master'

# time in seconds for dispatcher to check new jobs
DISPATCHER_SLEEP_TIME = 10
# storage class to be used by uploader script
SOURCE_MANAGER_CLASS = None # use default one
# where to store info about processes launched by the hub
RUN_DIR = './run'

