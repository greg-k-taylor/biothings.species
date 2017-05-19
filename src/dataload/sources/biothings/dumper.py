import os, sys, time, datetime, json
from urllib.parse import urlparse, urljoin
from functools import partial

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import HTTPDumper, DumperException
from biothings.utils.common import gunzipall, md5sum


class BiothingsDumper(HTTPDumper):
    """
    This dumper is used to maintain a BioThings API up-to-date. BioThings data
    is available as either as an ElasticSearch snapshot when full update,
    and a collection of diff files for incremental updates.
    It will either download incremental updates and apply diff, or trigger an ElasticSearch
    restore if the latest version is a full update.
    This dumper can also be configured with precedence rules: when a full and a incremental 
    update is available, rules can set so full is preferably used over incremental (size can also
    be considered when selecting the preferred way).
    
    """
    # App name for this biothings API. Must be set when using this dumper
    BIOTHINGS_APP = None

    SRC_NAME = "biothings"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # URL is always the same, but headers change (template for app + version)
    SRC_URL = "http://biothings-diffs.s3-website-us-east-1.amazonaws.com/%s/%s.json"

    # Auto-deploy data update ?
    AUTO_UPLOAD = False

    # Optionally, a schedule can be used to automatically check new version
    #SCHEDULE = "0 9 * * *"

    # what backend the dumper should work with. Must be defined before instantiation
    # (can be an instance or a partial() returning an instance
    TARGET_BACKEND = None

    # TODO: should we ensure ARCHIVE is always true ?
    # (ie we have to keep all versions to apply them in order)


    def __init__(self, *args, **kwargs):
        super(BiothingsDumper,self).__init__(*args,**kwargs)
        # list of build_version to download/apply, in order
        self.apply_builds = []
        self._target_backend = None

    @property
    def target_backend(self):
        if not self._target_backend:
            if type(self.__class__.TARGET_BACKEND) == partial:
                self._target_backend = self.__class__.TARGET_BACKEND()
            else:
                 self._target_backend = self.__class__.TARGET_BACKEND
        return self._target_backend

    def load_remote_json(self,url):
        res = self.client.get(url)
        if res.status_code != 200:
            return None
        try:
            jsondat = json.loads(res.text)
            return jsondat
        except json.JSONDecodeError:
            return None

    def remote_is_better(self,remotefile,localfile):
        # first check remote version, if not equals to our version, update is needed
        remote_dat = self.load_remote_json(remotefile)
        if not remote_dat:
            # we didn't get any json dat, which is weird, anyway remote is not better...
            return False
        remote_version = remote_dat["build_version"]
        # local version can be taken from backend, and it None (starting from scratch)
        # from src_dump (meaning we downloaded it but we did not apply it)
        local_version = self.target_backend.version or self.current_release
        self.logger.info("rmeove %s local %s" % (remote_version,local_version))
        # local_version None means we're starting from scratch.
        if local_version is None:
            return True
        if remote_version != local_version:
            # check the timestamp (maybe files were previously downloaded but not applied,
            # ie. version wasn't increased)
            # convert all in GMT to easily compare
            res = os.stat(localfile) # local file in local time
            local_lastmodified = datetime.datetime.utcfromtimestamp(res.st_mtime) # local file already in gmt time
            res = self.client.get(remotefile) # GET to follow redirection and get proper headers
            if res.status_code != 200:
                raise DumperException("%s, %s" % (res.status_code,res.reason))
            # S3 already returns last-modified in utc/gmt
            remote_lastmodified = datetime.datetime.utcfromtimestamp(int(res.headers["x-amz-meta-lastmodified"]))
            if remote_lastmodified > local_lastmodified:
                self.logger.debug("Remote file '%s' is newer (remote: %s, local: %s)" %
                        (remotefile,remote_lastmodified,local_lastmodified))
                return True
            else:
                self.logger.debug("Remote file '%s' is older (remote: %s, local: %s), nothings to do" %
                        (remotefile,remote_lastmodified,local_lastmodified))
                return False
        else:
            self.logger.info("Remote and local version ('%s') match, nothing to do" % remote_version)
            return False

    def create_todump_list(self, force=False, version="latest"):
        assert self.__class__.BIOTHINGS_APP, "BIOTHINGS_APP class attribute is not set"
        self.logger.info("Dumping version '%s'" % version)
        file_url = self.__class__.SRC_URL % (self.__class__.BIOTHINGS_APP,version)
        filename = os.path.basename(self.__class__.SRC_URL)
        try:
            current_localfile = os.path.join(self.current_data_folder,"%s.json" % self.current_release)
            # check it actually exists (if data folder was deleted by src_dump still refers to 
            # this folder, this file won't exist)
            if not os.path.exists(current_localfile):
                self.logger.error("Local file '%s' doesn't exists" % current_localfile)
                raise FileNotFoundError
        except (TypeError, FileNotFoundError) as e:
            # current data folder doesn't even exist
            self.logger.error("Can't determine local file: %s" % e)
            current_localfile = None
        if current_localfile is None or self.remote_is_better(file_url,current_localfile):
            # manually get the diff meta file (ie. not using download() because we don't know the version yet,
            # it's in the diff meta
            self.logger.info("file url : %s" % file_url)
            build_meta = self.load_remote_json(file_url)
            if not build_meta:
                raise Exception("Can't get remote build information about version '%s' (url was '%s')" % \
                        (version,file_url))
            # latest poins to a new version, 2 options there:
            # - update is a full snapshot: nothing to download, but we need to trigger a restore
            # - update is an incremental: 
            #   * we first need to check if the incremental is compatible with current version
            #     if not, we need to find the previous update (full or incremental) compatible
            #   * if compatible, we need to download metadata file which contains the list of files
            #     we need to download and then trigger a sync using those diff files
            if build_meta["type"] == "incremental":
                metadata = self.load_remote_json(build_meta["metadata"]["url"])
                if not metadata:
                    raise DumperException("Can't get metadata information about version '%s' (url is wrong ? '%s')" % \
                            (verison,build_meta["metadata"]["url"]))
                # old version contains the compatible version for which we can apply the diff
                # let's compare...
                if self.target_backend.version == metadata["old_version"]:
                    self.logger.info("Diff update version '%s' is compatible with current version, apply update" % metadata["old_version"])
                else:
                    self.logger.info("Diff update requires version '%s' but target_backend is '%s'. Now looking for a compatible version" % (metadata["old_version"],self.target_backend.version))
                    # keep track on this version, we'll need to apply it later
                    self.apply_builds.insert(0,build_meta["metadata"]["url"])
                    return self.create_todump_list(force=force,version=metadata["old_version"])
                self.release = build_meta["build_version"]
                # ok, now we can use download()
                # we will download it again during the normal process so we can then compare
                # when we have new data release
                new_localfile = os.path.join(self.new_data_folder,"%s.json" % self.release)
                self.to_dump.append({"remote":file_url, "local":new_localfile})
                # get base url (used later to get diff files)
                metadata_url = build_meta["metadata"]["url"]
                base_url = os.path.dirname(metadata_url) + "/" # "/" or urljoin will remove previous fragment...
                new_localfile = os.path.join(self.new_data_folder,os.path.basename(metadata_url))
                self.download(metadata_url,new_localfile)
                metadata = json.load(open(new_localfile))
                for md5_fname in metadata["diff_files"]:
                    fname = md5_fname["name"]
                    p = urlparse(fname)
                    if not p.scheme:
                        # this is a relative path
                        furl = urljoin(base_url,fname)
                    else:
                        # this is a true URL
                        furl = fname
                    new_localfile = os.path.join(self.new_data_folder,os.path.basename(fname))
                    self.to_dump.append({"remote":furl, "local":new_localfile}) 
            else:
                # it's a full snapshot release, it always can be applied
                self.release = build_meta["build_version"]
                new_localfile = os.path.join(self.new_data_folder,"%s.json" % self.release)
                self.to_dump.append({"remote":file_url, "local":new_localfile})

            # unset this one, as it may not be pickelable (next step is "download", which
            # uses different processes and need workers to be pickled)
            self._target_backend = None

    def post_dump(self):
        build_meta = json.load(open(os.path.join(self.new_data_folder,"%s.json" % self.release)))
        if build_meta["type"] == "incremental":
            self.logger.info("Checking md5sum for files in '%s'" % self.new_data_folder) 
            metadata = json.load(open(os.path.join(self.new_data_folder,"metadata.json")))
            for md5_fname in metadata["diff_files"]:
                spec_md5 = md5_fname["md5sum"]
                fname = md5_fname["name"]
                compute_md5 = md5sum(os.path.join(self.new_data_folder,fname))
                if compute_md5 != spec_md5:
                    self.logger.error("md5 check failed for file '%s', it may be corrupted" % fname)
                    e = DumperException("Bad md5sum for file '%s'" % fname)
                    self.register_status("failed",download={"err" : repr(e)})
                    raise e
                else:
                    self.logger.debug("md5 check success for file '%s'" % fname)

