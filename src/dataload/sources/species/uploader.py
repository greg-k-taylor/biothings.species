import os

import biothings.dataload.uploader as uploader
from .parser import parse_uniprot_speclist

class SpeciesUploader(uploader.BaseSourceUploader):

    name = "species"

    __metadata__ = {"mapper" : 'has_gene'}

    def load_data(self,data_folder):
        nodes_file = os.path.join(data_folder,"speclist.txt")
        self.logger.info("Load data from file '%s'" % nodes_file)
        return parse_uniprot_speclist(open(nodes_file))

