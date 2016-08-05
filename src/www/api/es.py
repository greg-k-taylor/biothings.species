# -*- coding: utf-8 -*-
from biothings.www.api.es import ESQuery
from biothings.www.api.es import ESQueryBuilder
from biothings.settings import BiothingSettings
from collections import OrderedDict
import datetime

bts = BiothingSettings()

MAX_TAXID_COUNT = 10000

class ESQuery(ESQuery):
    def _modify_biothingdoc(self, doc, options=None):
        # overriding this to insert children list, etc.
        if 'kwargs' in options and 'include_children' in options['kwargs'] and options['kwargs']['include_children']:
            doc['children'] = self.get_all_children_tax_ids(taxid=int(doc['_id']), has_gene=options['kwargs'].get('has_gene', False), include_self=False, raw=False)
        return doc

    def get_all_children_tax_ids(self, taxid, has_gene=True, include_self=False, raw=False):
        q = {
            'query': {
                "query_string": {}
            }
        }
        if has_gene:
            q['query']['query_string']['query'] = "lineage:{} AND has_gene:true".format(taxid)
        else:
            q['query']['query_string']['query'] = "lineage:{}".format(taxid)

        res = self._es.search(body=q, index=self._index, doc_type=self._doc_type, fields='_id', size=MAX_TAXID_COUNT)
        if raw:
            return res
        taxid_li = [int(x['_id']) for x in res['hits']['hits']]
        if include_self:
            if taxid not in taxid_li:
                taxid_li.append(taxid)
        elif taxid in taxid_li:
            taxid_li.remove(taxid)

        return sorted(taxid_li)

    def get_expanded_species_li(self, taxid_li):
        taxid_set = set()
        for taxid in taxid_li:
            taxid_set |= set(self.get_all_children_tax_ids(taxid))
            if len(taxid_set) >= MAX_TAXID_COUNT:
                break
        return sorted(taxid_set)[:MAX_TAXID_COUNT]

    def _populate_metadata(self):
        ''' Populate the metadata '''
        args = {
            "body": {
                "query": {
                    "match_all": {}
                },
                "aggs": {
                    "ranks": {
                        "terms": {
                            "field": "rank",
                            "size": 50
                        }
                    }
                }
            },
            "size": 0,
            "doc_type": "species"
        }
        r = self._es.search(**args)
        i = self._es.indices.get_settings(index=bts.es_index)
        m = self._es.indices.get_mapping(index=bts.es_index)
        m = m[list(m.keys())[0]]['mappings']
        total_tax_ids = r['hits']['total']
        taxonomic_distribution = dict([ (x['key'], x['doc_count']) for x in r['aggregations']['ranks']['buckets'] 
                                        if x['key'] != 'rank'])
        taxonomic_distribution['no rank'] = taxonomic_distribution['no']
        del(taxonomic_distribution['no'])
        creation_date = datetime.datetime.fromtimestamp(float(i[list(i.keys())[0]]['settings']['index']['creation_date'])/1000)
        ret = {
            "stats": {
                "unique taxonomy ids": total_tax_ids,
                "taxonomic distribution of ids": taxonomic_distribution
            },
            "timestamp": creation_date.strftime("%Y-%m-%dT%H:%M:%S")
        }
        m[bts.es_doc_type]['_meta'] = ret
        self._es.indices.put_mapping(index=bts.es_index, doc_type=bts.es_doc_type,body=m)
        return ret

    def mget_biothings(self, bid_list, **kwargs):
        '''for /query post request'''
        options = self._get_cleaned_query_options(kwargs)
        expand = options.get('kwargs', {}).pop('expand_species', False)
        if expand:
            return self.get_expanded_species_li(bid_list)
        qbdr = ESQueryBuilder(**options.kwargs)
        try:
            _q = qbdr.build_multiple_id_query(bid_list, scopes=options.scopes)
        except QueryError as err:
            return {'success': False,
                    'error': err.message}
        if options.rawquery:
            return _q
        res = self._es.msearch(body=_q, index=self._index, doc_type=self._doc_type)['responses']
        if options.raw:
            return res

        assert len(res) == len(bid_list)
        _res = []

        for i in range(len(res)):
            hits = res[i]
            qterm = bid_list[i]
            hits = self._cleaned_res(hits, empty=[], single_hit=False, options=options)
            if len(hits) == 0:
                _res.append({u'query': qterm,
                             u'notfound': True})
            elif 'error' in hits:
                _res.append({u'query': qterm,
                             u'error': True})
            else:
                for hit in hits:
                    hit[u'query'] = qterm
                    _res.append(hit)
        return _res
