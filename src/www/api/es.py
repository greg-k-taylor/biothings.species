# -*- coding: utf-8 -*-
from biothings.www.api.es import ESQuery
from biothings.www.api.es import ESQueryBuilder
from collections import OrderedDict
import datetime

MAX_TAXID_COUNT = 10000

class ESQuery(ESQuery):
    def _get_options(self, options, kwargs):
        options.include_children = kwargs.pop('include_children', False)
        options.has_gene = kwargs.pop('has_gene', False)
        options.expand_species = kwargs.pop('expand_species', False)
        return options

    def _modify_biothingdoc(self, doc, options=None):
        # overriding this to insert children list, etc.
        if options.include_children:
            doc['children'] = self.get_all_children_tax_ids(taxid=int(doc['_id']), has_gene=options.has_gene, include_self=False, raw=False)
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
            "doc_type": self._doc_type
        }
        r = self._es.search(**args)
        m = self._es.indices.get_mapping(index=self._index)
        i = self._es.indices.get_settings(index=self._index)
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
                "distribution of taxonomy ids by rank": taxonomic_distribution
            },
            "timestamp": creation_date.strftime("%Y-%m-%dT%H:%M:%S")
        }
        m[self._doc_type]['_meta'] = ret
        self._es.indices.put_mapping(index=self._index, doc_type=self._doc_type,body=m)
        return ret

    def mget_biothings(self, bid_list, **kwargs):
        '''for /query post request'''
        options = self._get_cleaned_query_options(kwargs)
        if options.expand_species:
            return self.get_expanded_species_li(bid_list)
        return self.mcommon_biothings(bid_list, options, **kwargs)
