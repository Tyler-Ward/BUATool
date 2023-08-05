#!/usr/bin/python3

import os
import datetime
from .plugins.sha1.main import Sha1Checksum
from .plugins.media_checksum.main import MediaChecksum


class DirectoryIndex:
    index = None
    indexed_on = None
    directory_path = None
    features = list()

    def generateIndex(self, directory, features=[]):
        """Populates the index for a target directory"""

        self.index = []
        self.indexed_on = datetime.datetime.now()
        self.directory_path = os.path.abspath(directory)
        self.features = list()

        # create main index
        for (dirpath, dirnames, filenames) in os.walk(directory):
            # extract relative path within index
            relpath = dirpath[len(directory):] if dirpath.startswith(directory) else dirpath
            for filename in filenames:
                try:
                    filedetails = {
                            'name': filename,
                            'folder': relpath,
                            'path': relpath+"/"+filename if relpath else filename,
                            }
                    self.index.append(filedetails)
                except (FileNotFoundError, PermissionError):
                    print("Unable to index "+dirpath+"/"+filename)

        # process additional feautures
        if "sha1" in features:
            self.calculateChecksums()
        if "media_checksum" in features:
            self.calculateMediaChecksums()

    def calculateChecksums(self):
        import progressbar

        self.features.append("sha1")

        bar = progressbar.ProgressBar(max_value=len(self.index), redirect_stdout=True)

        for filedetails in self.index:
            try:
                # print(filedetails["fullpath"])
                filedetails['sha1'] = SHA1Checksup.generateFileData(self.directory_path + "/" + filedetails["path"])
            except (ValueError, FileNotFoundError, PermissionError):
                print("Unable to calculate checksum for ", self.directory_path + "/" + filedetails["path"])
            bar.update(bar.value+1)

    def calculateMediaChecksums(self):
        import progressbar

        self.features.append("media_checksum")

        bar = progressbar.ProgressBar(max_value=len(self.index), redirect_stdout=True)

        for filedetails in self.index:
            try:
                csum = MediaChecksum.generateFileData(self.directory_path + "/" + filedetails["path"])
                if csum is not None:
                    filedetails['media_checksum'] = csum
            except (ValueError, FileNotFoundError, PermissionError):
                print("Unable to calculate checksum for ", self.directory_path + "/" + filedetails["path"])
            bar.update(bar.value+1)

    def findFile(self, name):
        return (list(filter(lambda filed: filed['name'] == name, self.index)))

    def findValue(self, field, value):
        if value is None:
            return list()
        return (list(filter(lambda filed: field in filed and filed[field] == value, self.index)))

    def saveIndex(self, location):
        import json
        with open(location, "w") as output:
            output_data = {
                "directory": self.directory_path,
                "indexed_on": self.indexed_on.isoformat(),
                "features": self.features,
                "length": len(self.index),
                "index": self.index,
                }
            json.dump(output_data, output)

    def loadIndex(self, location):
        import json
        with open(location, "r") as indexInput:
            data = json.load(indexInput)
            self.directory_path = data["directory"]
            self.features = data["features"]
            self.indexed_on = data["indexed_on"]
            self.index = data["index"]
