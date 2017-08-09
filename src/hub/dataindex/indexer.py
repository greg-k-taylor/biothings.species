import biothings.hub.dataindex.indexer as indexer


class TaxonomyIndexer(indexer.Indexer):

    def get_mapping(self, enable_timestamp=True):
        mapping = super(TaxonomyIndexer,self).get_mapping(enable_timestamp=enable_timestamp)                                                                                                                                             
        mapping["properties"]["lineage"] = { 
                "include_in_all": False,
                "type": "long"
                }

        return mapping
