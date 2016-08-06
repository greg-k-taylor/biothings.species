# -*- coding: utf-8 -*-
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, StatusHandler, FieldsHandler
from biothings.settings import BiothingSettings
from collections import OrderedDict

bts = BiothingSettings()

class SpeciesHandler(BiothingHandler):
    ''' This class is for the /species endpoint. '''
    boolean_parameters = set(['raw', 'rawquery', 'explain', 'include_children', 'has_gene', 'expand_species', 'jsonld', 'dotfield'])
    
class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    boolean_parameters = set(['raw', 'rawquery', 'fetch_all', 'explain', 'include_children', 'has_gene', 'expand_species', 'jsonld', 'dotfield'])

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''

class FieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''

class MetaDataHandler(MetaDataHandler):
    ''' This class is for the /metadata endpoint. '''
    def get(self):
        kwargs = self.get_query_params()
        _meta = self.esq.get_mapping_meta(**kwargs)
        _meta['stats'] = OrderedDict([('unique taxonomy ids',_meta['stats']['unique taxonomy ids']),
            ('distribution of taxonomy ids by rank', OrderedDict([(k,v) for (k,v) in sorted(
                _meta['stats']['distribution of taxonomy ids by rank'].items(), key=lambda i: i[1], reverse=True)]))])
        self._fill_software_info(_meta)
        self.return_json(_meta)

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
