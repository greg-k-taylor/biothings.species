# -*- coding: utf-8 -*-
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, StatusHandler, FieldsHandler
from biothings.settings import BiothingSettings
from www.api.es import ESQuery
import config

biothing_settings = BiothingSettings()

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
    if biothing_settings._api_version:
        ret += [
            (r"/" + biothing_settings._api_version + "/metadata", MetaDataHandler),
            (r"/" + biothing_settings._api_version + "/metadata/fields", FieldsHandler),
            (r"/" + biothing_settings._api_version + "/species/(.+)/?", SpeciesHandler),
            (r"/" + biothing_settings._api_version + "/species/?$", SpeciesHandler),
            (r"/" + biothing_settings._api_version + "/query/?", QueryHandler),
        ]
    else:
        ret += [
            (r"/species/(.+)/?", SpeciesHandler),
            (r"/species/?$", SpeciesHandler),
            (r"/query/?", QueryHandler),
        ]
    return ret
