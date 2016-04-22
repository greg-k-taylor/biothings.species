# -*- coding: utf-8 -*-
# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = '52.33.60.29:9200'
# elasticsearch index name
ES_INDEX_NAME = 'myspecies_current'
# elasticsearch document type
ES_DOC_TYPE = 'species'
# Only these options are passed to the elasticsearch query from kwargs
ALLOWED_OPTIONS = ['_source', 'start', 'from_', 'size',
                   'sort', 'explain', 'version', 'facets']
ES_SCROLL_TIME = '1m'
ES_SCROLL_SIZE = 1000
ES_QUERY_MODULE = 'www.api.es'

# *****************************************************************************
# Google Analytics Settings
# *****************************************************************************
# Google Analytics Account ID
GA_ACCOUNT = ''
# Turn this to True to start google analytics tracking
GA_RUN_IN_PROD = False

# 'category' in google analytics event object
GA_EVENT_CATEGORY = 'v1_api'
# 'action' for get request in google analytics event object
GA_EVENT_GET_ACTION = 'get'
# 'action' for post request in google analytics event object
GA_EVENT_POST_ACTION = 'post'
# url for google analytics tracker
GA_TRACKER_URL = 'MySpecies.info'

# *****************************************************************************
# URL settings
# *****************************************************************************
# For URL stuff
ANNOTATION_ENDPOINT = 'species'
QUERY_ENDPOINT = 'query'
API_VERSION = 'v1'
# TODO Fill in a status id here
STATUS_CHECK_ID = '9606'
# Path to a file containing a json object with information about elasticsearch fields
FIELD_NOTES_PATH = ''
JSONLD_CONTEXT_PATH = ''
NOSETEST_SETTINGS = 'tests.nosetest_config'
