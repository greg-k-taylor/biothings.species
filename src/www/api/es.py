# -*- coding: utf-8 -*-
from biothings.www.api.es import ESQuery

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

    def mget_biothings(self, bid_list, **kwargs):
        '''for /query post request'''
        options = self._get_cleaned_query_options(kwargs)
        if 'kwargs' in options and 'expand_species' in options['kwargs'] and options['kwargs']['expand_species']:
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
