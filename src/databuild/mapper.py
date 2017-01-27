import biothings, config
biothings.config_for_app(config)
from biothings.utils.common import loadobj
import biothings.utils.mongo as mongo
import biothings.databuild.mapper as mapper
# just to get the collection name
from dataload.sources.geneinfo.uploader import GeneInfoUploader


class HasGeneMapper(mapper.BaseMapper):

    def __init__(self, *args, **kwargs):
        super(HasGeneMapper,self).__init__(*args,**kwargs)
        self.cache = None

    def load(self):
        if self.cache is None:
            # this is a whole dict containing all taxonomu _ids
            col = mongo.get_src_db()[GeneInfoUploader.name]
            self.cache = [d["_id"] for d in col.find({},{"_id":1})]

    def process(self,docs):
        for doc in docs:
            if doc["_id"] in self.cache:
                doc["has_gene"] = True
            yield doc

