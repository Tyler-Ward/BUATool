#!/usr/bin/python3

import os
import datetime


class DirectoryIndex:
    index = None
    indexed_on = None
    directory_path = None
    features = list()

    def generateIndex(self, directory, plugins=[]):
        """Populates the index for a target directory"""

        self.index = []
        self.indexed_on = datetime.datetime.now()
        self.directory_path = os.path.abspath(directory)
        self.features = list()

        # create main index
        self.generateFileList()

        # process pluggins
        for plugin in plugins:
            self.processPlugin(plugin)

    def updateIndex(self, directory=None, plugins=[]):

        oldindex = self.index.copy()
        oldfeatures = self.features.copy()

        self.indexed_on = datetime.datetime.now()
        self.features = list()

        if directory and directory != "":
            if directory != self.directory_path:
                print("updating index path")
                self.directory_path = os.path.abspath(directory)

        # todo check plugins

        # create new index
        self.generateFileList()

        # import old data
        files_to_generate = []

        for fileid, filedetails in enumerate(self.index):
            previous = list(filter(lambda filed: filed['path'] == filedetails["path"], oldindex))
            if previous and previous[0].get("modified",0)==filedetails["modified"]:
                filedetails = previous[0]
            else:
                files_to_generate.append(fileid)



        # process pluggins
        for plugin in plugins:
            if plugin.name in oldfeatures:
                import progressbar
                print("Updating {}".format(plugin.name))
                self.features.append(plugin.name)

                bar = progressbar.ProgressBar(max_value=len(files_to_generate), redirect_stdout=True)
                for fileid in files_to_generate:
                    filedetails = self.index[fileid]
                    try:
                        filedetails[plugin.name] = plugin.generateFileData(self.directory_path + "/" + filedetails["path"])
                    except (ValueError, FileNotFoundError, PermissionError):
                        print("Unable to calculate {} plugin data for {}/{}".format(plugin.name,self.directory_path,filedetails["path"]))
                    bar.update(bar.value+1)
            else:
                self.processPlugin(plugin)


    def generateFileList(self):
        self.index = []
        for (dirpath, dirnames, filenames) in os.walk(self.directory_path):
            # extract relative path within index
            relpath = dirpath[len(self.directory_path):] if dirpath.startswith(self.directory_path) else dirpath
            for filename in filenames:
                try:
                    filepath = relpath+"/"+filename if relpath else filename
                    filedetails = {
                            'name': filename,
                            'folder': relpath,
                            'path': filepath,
                            'modified': os.path.getmtime(self.directory_path+"/"+filepath)
                            }
                    self.index.append(filedetails)
                except (FileNotFoundError, PermissionError):
                    print("Unable to index {}".format(fullpath))


    def processPlugin(self, plugin):
        import progressbar
        print("Processing {}".format(plugin.name))
        self.features.append(plugin.name)

        bar = progressbar.ProgressBar(max_value=len(self.index), redirect_stdout=True)

        for filedetails in self.index:
            try:
                filedetails[plugin.name] = plugin.generateFileData(self.directory_path + "/" + filedetails["path"])
            except (ValueError, FileNotFoundError, PermissionError):
                print("Unable to calculate {} plugin data for {}/{}".format(plugin.name,self.directory_path,filedetails["path"]))
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
