from biothings.utils.mongo import doc_feeder, get_target_db
from biothings.databuild.builder import DataBuilder
from biothings.dataload.storage import UpsertStorage
import config

class TaxonomyDataBuilder(DataBuilder):

    def post_merge(self, source_names, batch_size, job_manager):
        # get the lineage mapper
        mapper = self.mappers["lineage"]
        # load cache (it's being loaded automatically
        # as it's not part of an upload process
        mapper.load()

        # create a storage to save docs back to merged collection
        db = get_target_db()
        col_name = self.target_backend.target_collection.name
        storage = UpsertStorage(db,col_name)

        for docs in doc_feeder(self.target_backend.target_collection, step=batch_size):
            docs = mapper.process(docs)
            storage.process(docs,batch_size)



