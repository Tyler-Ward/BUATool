#!/usr/bin/python3

import os
import sys
import filecmp
import datetime
from .util import calculateSHA1Sum


class DirectoryIndex:
    index = None
    indexed_on = None
    directory_path = None
    features = list()

    def generateIndex(self,directory,sha1=False):
        """Populates the index for a target directory"""

        self.index=[]
        self.indexed_on = datetime.datetime.now()
        self.directory_path = os.path.abspath(directory)

        for (dirpath, dirnames, filenames) in os.walk(directory):
            # extract relative path within index
            relpath = dirpath[len(directory):] if dirpath.startswith(directory) else dirpath
            for filename in filenames:
                try:
                    filedetails={
                            'name':filename,
                            'folder':relpath,
                            'path':relpath+"/"+filename if relpath else filename,
                            }
                    self.index.append(filedetails)
                except (FileNotFoundError,PermissionError):
                    print("Unable to index "+dirpath+"/"+filename)
        if sha1:
            self.calculateChecksums()


    def calculateChecksums(self):
        import progressbar

        self.features.append("sha1")

        bar = progressbar.ProgressBar(max_value=len(self.index),redirect_stdout=True)

        for filedetails in self.index:
            try:
                # print(filedetails["fullpath"])
                filedetails['sha1']=calculateSHA1Sum(self.directory_path + "/" + filedetails["path"])
            except (ValueError,FileNotFoundError,PermissionError):
                print("Unable to calculate checksum for ",self.directory_path + "/" + filedetails["path"])
            bar.update(bar.value+1)

    def findFile(self,name):
        return(list(filter(lambda filed: filed['name'] == name,self.index)))

    def findHash(self,sha1):
        return(list(filter(lambda filed: 'sha1' in filed and filed['sha1'] == sha1,self.index)))

    def saveIndex(self,location):
        import json
        with open(location,"w") as output:
            output_data = {
                "directory" : self.directory_path,
                "indexed_on" : self.indexed_on.isoformat(),
                "features" : self.features,
                "length" : len(self.index),
                "index" : self.index,
                }
            json.dump(output_data,output)

    def loadIndex(self,location):
        import json
        with open(location,"r") as indexInput:
            data = json.load(indexInput)
            self.directory_path = data["directory"]
            self.features = data["features"]
            self.indexed_on = data["indexed_on"]
            self.index = data["index"]
