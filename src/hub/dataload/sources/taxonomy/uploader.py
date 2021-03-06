import os

import biothings.hub.dataload.uploader as uploader
from .parser import parse_refseq_names, parse_refseq_nodes


class TaxonomyNodesUploader(uploader.BaseSourceUploader):

    main_source = "taxonomy"
    name = "nodes"

    def load_data(self,data_folder):
        nodes_file = os.path.join(data_folder,"nodes.dmp")
        self.logger.info("Load data from file '%s'" % nodes_file)
        return parse_refseq_nodes(open(nodes_file))

    @classmethod
    def get_mapping(klass):
        return {
                "rank": {
                    "include_in_all": False,
                    "type": "string"
                    },
                "taxid": {
                    "include_in_all": True,
                    "type": "long"
                    },
                "parent_taxid": {
                    "include_in_all": False,
                    "type": "long"
                    },
                }


class TaxonomyNamesUploader(uploader.BaseSourceUploader):

    main_source = "taxonomy"
    name = "names"
    __metadata__ = {"mapper" : 'has_gene'}

    def load_data(self,data_folder):
        names_file = os.path.join(data_folder,"names.dmp")
        self.logger.info("Load data from file '%s'" % names_file)
        return parse_refseq_names(open(names_file))

    @classmethod
    def get_mapping(klass):
        return {
                "scientific_name": {
                    "include_in_all": True,
                    "type": "string"
                    },
                "common_name": {
                    "include_in_all": True,
                    "type": "string"
                    },
                "genbank_common_name": {
                    "include_in_all": False,
                    "type": "string"
                    }
                }

