import hashlib
import os
import filecmp


class Sha1Checksum:
    """
      BUA tool plugin to compare the contents of media files

      This plugin will create a checkum of a media files contents to alloww matching of media files with altered metadata
    """

    name = "sha1"

    @staticmethod
    def generateFileData(filename):
        sha1 = hashlib.sha1()
        if (not os.path.isfile(filename)):
            raise ValueError("Provided path is not a file")
        with open(filename, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    @staticmethod
    def findMatches(filename, index):

        matches = []
        
        filesha1 = Sha1Checksum.generateFileData(filename)
        if filesha1 == "da39a3ee5e6b4b0d3255bfef95601890afd80709":
            filesha1 = None
        
        hashmatches = index.findValue("sha1", filesha1)
        for checksum_match in hashmatches:
            if filecmp.cmp(filename, index.directory_path + "/" + checksum_match['path']):
                matches.append(("Renamed", checksum_match))

        return matches
