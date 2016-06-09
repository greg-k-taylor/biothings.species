# -*- coding: utf-8 -*-
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, StatusHandler, FieldsHandler
from biothings.settings import BiothingSettings
from www.api.es import ESQuery
#import config

bts = BiothingSettings()

class SpeciesHandler(BiothingHandler):
    ''' This class is for the /species endpoint. '''
    boolean_parameters = set(['raw', 'rawquery', 'fetch_all', 'explain', 'include_children', 'has_gene', 'expand_species'])

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''

class FieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''

class MetaDataHandler(MetaDataHandler):
    ''' This class is for the /metadata endpoint. '''


def return_applist():
    ret = [
        (r"/status", StatusHandler),
        (r"/metadata", MetaDataHandler),
        (r"/metadata/fields", FieldsHandler),
    ]
    if bts._api_version:
        ret += [
            (r"/" + bts._api_version + "/metadata", MetaDataHandler),
            (r"/" + bts._api_version + "/metadata/fields", FieldsHandler),
            (r"/" + "/".join([bts._api_version, bts._annotation_endpoint, "(.+)", "?"]), SpeciesHandler),
            (r"/" + "/".join([bts._api_version, bts._annotation_endpoint, "?$"]), SpeciesHandler),
            (r"/" + "/".join([bts._api_version, bts._query_endpoint, "?"]), QueryHandler),
        ]
    else:
        ret += [
            (r"/" + bts._annotation_endpoint + "/(.+)/?", SpeciesHandler),
            (r"/" + bts._annotation_endpoint + "/?$", SpeciesHandler),
            (r"/" + bts._query_endpoint + "/?", QueryHandler),
        ]
    return ret
