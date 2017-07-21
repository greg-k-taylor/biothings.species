# -*- coding: utf-8 -*-
from biothings.web.api.es.handlers import BiothingHandler
from biothings.web.api.es.handlers import MetadataHandler
from biothings.web.api.es.handlers import QueryHandler
from biothings.web.api.es.handlers import StatusHandler
#import logging

def pre_query_builder_hook(inst, options):
    options['transform_kwargs']['index'] = inst._get_es_index(options)
    options['transform_kwargs']['doc_type'] = inst._get_es_doc_type(options)
    options['transform_kwargs']['es_client'] = inst.web_settings.es_client
    return options

class TaxonHandler(BiothingHandler):
    ''' This class is for the /taxon endpoint. '''
    def _pre_query_builder_GET_hook(self, options):
        return pre_query_builder_hook(self, options)

    def _pre_query_builder_POST_hook(self, options):
        return pre_query_builder_hook(self, options)

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    def _pre_query_builder_GET_hook(self, options):
        return pre_query_builder_hook(self, options)

    def _pre_query_builder_POST_hook(self, options):
        return pre_query_builder_hook(self, options)

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    pass

class MetadataHandler(MetadataHandler):
    ''' This class is for the /metadata endpoint. '''
    pass
