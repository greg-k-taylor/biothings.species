# -*- coding: utf-8 -*-
import os
from biothings.www.settings.default import *
from www.api.query_builder import ESQueryBuilder
from www.api.query import ESQuery
from www.api.transform import ESResultTransformer
from www.api.handlers import TaxonHandler, QueryHandler, MetadataHandler, StatusHandler

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = 'localhost:9200'
# elasticsearch index name
ES_INDEX = 'taxonomy'
# elasticsearch document type
ES_DOC_TYPE = 'taxon'
# defautlt number_of_shards when create a new index
ES_NUMBER_OF_SHARDS = 5

API_VERSION = 'v1'

# *****************************************************************************
# App URL Patterns
# *****************************************************************************
APP_LIST = [
    (r"/status", StatusHandler),
    (r"/metadata/?", MetadataHandler),
    (r"/metadata/fields/?", MetadataHandler),
    (r"/{}/taxon/(.+)/?".format(API_VERSION), TaxonHandler),
    (r"/{}/taxon/?$".format(API_VERSION), TaxonHandler),
    (r"/{}/query/?".format(API_VERSION), QueryHandler),
    (r"/{}/metadata/?".format(API_VERSION), MetadataHandler),
    (r"/{}/metadata/fields/?".format(API_VERSION), MetadataHandler),
]

###############################################################################
#   app-specific query builder, query, and result transformer classes
###############################################################################

# *****************************************************************************
# Subclass of biothings.www.api.es.query_builder.ESQueryBuilder to build
# queries for this app
# *****************************************************************************
ES_QUERY_BUILDER = ESQueryBuilder
# *****************************************************************************
# Subclass of biothings.www.api.es.query.ESQuery to execute queries for this app
# *****************************************************************************
ES_QUERY = ESQuery
# *****************************************************************************
# Subclass of biothings.www.api.es.transform.ESResultTransformer to transform
# ES results for this app
# *****************************************************************************
ES_RESULT_TRANSFORMER = ESResultTransformer

GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'species_get'
GA_ACTION_ANNOTATION_POST = 'species_post'
GA_TRACKER_URL = 't.biothings.io'

HIPCHAT_MESSAGE_COLOR = 'purple'

STATUS_CHECK_ID = ''

# KWARGS for taxon API
DEFAULT_FALSE_BOOL_TYPEDEF = {'default': False, 'type': bool}
ANNOTATION_GET_TRANSFORM_KWARGS.update({'include_children': DEFAULT_FALSE_BOOL_TYPEDEF, 
                                        'has_gene': DEFAULT_FALSE_BOOL_TYPEDEF})
ANNOTATION_POST_TRANSFORM_KWARGS.update({'include_children': DEFAULT_FALSE_BOOL_TYPEDEF,
                                        'has_gene': DEFAULT_FALSE_BOOL_TYPEDEF,
                                        'expand_species': DEFAULT_FALSE_BOOL_TYPEDEF})
QUERY_GET_TRANSFORM_KWARGS.update({'include_children': DEFAULT_FALSE_BOOL_TYPEDEF,
                                    'has_gene': DEFAULT_FALSE_BOOL_TYPEDEF})
QUERY_POST_TRANSFORM_KWARGS.update({'include_children': DEFAULT_FALSE_BOOL_TYPEDEF,
                                    'has_gene': DEFAULT_FALSE_BOOL_TYPEDEF})

#############
# HUB VARS  #
#############

DATA_HUB_DB_DATABASE = "hub_config"                       # db containing the following (internal use)
DATA_SRC_MASTER_COLLECTION = 'src_master'             # for metadata of each src collections
DATA_SRC_DUMP_COLLECTION = 'src_dump'                 # for src data download information
DATA_SRC_BUILD_COLLECTION = 'src_build'               # for src data build information
DATA_SRC_BUILD_CONFIG_COLLECTION = 'src_build_config' # for src data build configuration

DATA_TARGET_MASTER_COLLECTION = 'db_master'

# Internal backend. Default to mongodb
# For now, other options are: sqlite3
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.sqlite3",
#        "sqlite_db_foder" : "./db",
#        }
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.mongo",
#        "uri" : "mongodb://localhost:27017",
#        #"uri" : "mongodb://user:passwd@localhost:27017", # mongodb std URI
#        }
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.es",
#        "host" : "localhost:9200",
#        }

# reporting diff results, number of IDs to consider (to avoid too much mem usage)
MAX_REPORTED_IDS = 1000
# for diff updates, number of IDs randomly picked as examples when rendering the report
MAX_RANDOMLY_PICKED = 10

# where to store info about processes launched by the hub
RUN_DIR = './run'

# Max queued jobs in job manager
# this shouldn't be 0 to make sure a job is pending and ready to be processed
# at any time (avoiding job submission preparation) but also not a huge number
# as any pending job will consume some memory).
MAX_QUEUED_JOBS = os.cpu_count() * 4 

# when creating a snapshot, how long should we wait before querying ES
# to check snapshot status/completion ? (in seconds)
MONITOR_SNAPSHOT_DELAY = 10

# compressed cache files
CACHE_FORMAT = "xz"

# Hub environment (like, prod, dev, ...)
# Used to generate remote metadata file, like "latest.json", "versions.json"
# If non-empty, this constant will be used to generate those url, as a prefix 
# with "-" between. So, if "dev", we'll have "dev-latest.json", etc...
# "" means production
HUB_ENV = ""

# default logger for the hub
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging

# If you need notifications to hipchat, fill with "token", 
# "roomid" and "from" keys to broadcast message to a Hipchat room.
HIPCHAT_CONFIG = {
        #    'token': 'abdce',
        #    'roomid': 123456,
        #    'from': 'hub'
        }

########################################
# APP-SPECIFIC CONFIGURATION VARIABLES #
########################################
# The following variables should or must be defined in your
# own application. Create a config.py file, import that config_common
# file as:
#
#   from config_common import *
#
# then define the following variables to fit your needs. You can also override any
# any other variables in this file as required. Variables defined as ValueError() exceptions
# *must* be defined
#
from biothings import ConfigurationError
# To be defined at application-level:

# Individual source database connection
DATA_SRC_SERVER = ConfigurationError("Define hostname for source database")
DATA_SRC_PORT = ConfigurationError("Define port for source database")
DATA_SRC_DATABASE = ConfigurationError("Define name for source database")
DATA_SRC_SERVER_USERNAME = ConfigurationError("Define username for source database connection (or None if not needed)")
DATA_SRC_SERVER_PASSWORD = ConfigurationError("Define password for source database connection (or None if not needed)")

# Target (merged collection) database connection
DATA_TARGET_SERVER = ConfigurationError("Define hostname for target database (merged collections)")
DATA_TARGET_PORT = ConfigurationError("Define port for target database (merged collections)")
DATA_TARGET_DATABASE = ConfigurationError("Define name for target database (merged collections)")
DATA_TARGET_SERVER_USERNAME = ConfigurationError("Define username for target database connection (or None if not needed)")
DATA_TARGET_SERVER_PASSWORD = ConfigurationError("Define password for target database connection (or None if not needed)")

# Hub database, defaulting to mongo, see HUB_DB_BACKEND above for more options
# You will need to provide a validb mongodb:// URI
HUB_DB_BACKEND = ConfigurationError("Define Hub DB connection")
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.mongo",
#        "uri" : "mongodb://localhost:27017",
#        #"uri" : "mongodb://user:passwd@localhost:27017", # mongodb std URI
#        }

# Path to a folder to store all downloaded files, logs, caches, etc...
DATA_ARCHIVE_ROOT = ConfigurationError("Define path to folder which will contain all downloaded data, cache files, etc...")
# this dir must be created manually
LOG_FOLDER = ConfigurationError("Define path to folder which will contain log files")
# Usually inside DATA_ARCHIVE_ROOT
#LOG_FOLDER = os.path.join(DATA_ARCHIVE_ROOT,'logs')

