# -*- coding: utf-8 -*-
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
