import os, asyncio
import json
from functools import partial

from elasticsearch.exceptions import NotFoundError, TransportError

from biothings import config as btconfig
import biothings.dataload.uploader as uploader
from biothings.utils.backend import DocESBackend
from biothings.utils.es import IndexerException

class BiothingsUploader(uploader.BaseSourceUploader):

    name = "biothings"

    # what backend the dumper should work with. Must be defined before instantiation
    # (can be an instance or a partial() returning an instance
    TARGET_BACKEND = None

    # should we delete index before restoring snapshot if index already exist ?
    AUTO_PURGE_INDEX = False


    def __init__(self, *args, **kwargs):
        super(BiothingsUploader,self).__init__(*args,**kwargs)
        self._target_backend = None

    @property
    def target_backend(self):
        if not self._target_backend:
            if type(self.__class__.TARGET_BACKEND) == partial:
                self._target_backend = self.__class__.TARGET_BACKEND()
            else:
                 self._target_backend = self.__class__.TARGET_BACKEND
            assert type(self._target_backend) == DocESBackend, "Only ElasticSearch backend is supported (got %s)" % type(self._target_backend)
        return self._target_backend

    @asyncio.coroutine
    def update_data(self, batch_size, job_manager):
        """
        Look in data_folder and either restore a snapshot to ES
        or apply diff to current ES index
        """
        got_error = False
        # determine if it's about a snapshot/full and diff/incremental
        # we should have a json metadata matching the release
        self.prepare_src_dump() # load infor from src_dump
        release = self.src_doc.get("release")
        build_meta = json.load(open(os.path.join(self.data_folder,"%s.json" % release)))
        if build_meta["type"] == "full":
            return self.restore_snapshot(build_meta,job_manager=job_manager)
        elif build_meta["type"] == "incremental":
            self.apply_diff(build_meta)

    def restore_snapshot(self,build_meta, job_manager):
        idxr = self.target_backend.target_esidxer
        # first check if snapshot repo exists
        repo_name, repo_settings = list(build_meta["metadata"]["repository"].items())[0]
        try:
            repo = idxr.get_repository(repo_name)
            # ok it exists, check if settings are the same
            if repo[repo_name] != repo_settings:
                # different, raise exception so it's handles in the except
                self.logger.info("Repository '%s' was found but settings are different, it needs to be created again" % repo_name)
                raise IndexerException
        except IndexerException:
            # okgg, it doesn't exist let's try to create it
            try:
                repo = idxr.create_repository(repo_name,repo_settings)
            except IndexerException as e:
                raise uploader.ResourceError("Could not create snapshot repository. Check elasticsearch.yml configuration " + \
                        "file, you should have a line like this: " + \
                        'repositories.url.allowed_urls: "%s*" ' % repo_settings["settings"]["url"] + \
                        "allowing snapshot to be restored from this URL. Error was: %s" % e)

        # repository is now ready, let's trigger the restore
        snapshot_name = build_meta["metadata"]["snapshot_name"]
        pinfo = self.get_pinfo()
        pinfo["step"] = "restore"
        pinfo["description"] = snapshot_name

        def get_status():
            try:
                res = idxr.get_restore_status(snapshot_name)
                return res["status"]
            except Exception as e:
                # somethng went wrong, report as failure
                return "FAILED %s" % e

        def restore_launched(f):
            try:
                self.logger.info("Restore launched: %s" % f.result())
            except Exception as e:
                self.logger.error("Error while lauching restore: %s" % e)
                raise e

        self.logger.info("Restoring snapshot '%s' on host '%s'" % (snapshot_name,idxr.es_host))
        job = yield from job_manager.defer_to_thread(pinfo,
                partial(idxr.restore,repo_name,snapshot_name,purge=self.__class__.AUTO_PURGE_INDEX))
        job.add_done_callback(restore_launched)
        yield from job
        while True:
            state = get_status()
            if state in ["INIT","IN_PROGRESS"]:
                yield from asyncio.sleep(getattr(btconfig,"MONITOR_SNAPSHOT_DELAY",60))
            else:
                if state == "DONE":
                    self.logger.info("Snapshot '%s' successfully restored (host: '%s')" % \
                            (snapshot_name,idxr.es_host),extra={"notify":True})
                else:
                    e = uploader.ResourceError("Restore failed for snapshot '%s', state: %s" % (snapshot_name,state))
                    self.logger.error("Failed restoring snaphost '%s' on host '%s': %s" % \
                        (snapshot_name,idxr.es_host,e))
                    raise e
                break

