#!/bin/python3

import os
import sys
import filecmp
import hashlib



def calculateSHA1Sum(filename):
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def generateLibraryRecords(directory):
    """Create a library record for a target directory"""

    fileindex=[]

    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            filedetails={
                    'name':filename,
                    'folder':dirpath,
                    'fullpath':dirpath+"/"+filename,
                    'sha1':calculateSHA1Sum(dirpath+"/"+filename)
                    }
            fileindex.append(filedetails)
    return fileindex


def findFile(name,index):
    return(list(filter(lambda filed: filed['name'] == name,index)))

def findHash(sha1,index):
    return(list(filter(lambda filed: filed['sha1'] == sha1,index)))

def findMatches(filename,filedir,index):

    matches = []
    filesha1 = calculateSHA1Sum(filedir+"/"+filename)

    namematches = findFile(filename,index)
    for match in namematches:
        if filesha1 == match['sha1']:
            if filecmp.cmp(filedir+"/"+filename,match['fullpath']):
                matches.append(match)
    if len(matches)>0:
        return matches

    hashmatches = findHash(filesha1,index)
    for match in hashmatches:
        if filecmp.cmp(filedir+"/"+filename,match['fullpath']):
            matches.append(match)

    return matches




def evaluateDirectory(directory,index):
    """Evaluates a directory an produces a result list"""

    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            matches = findMatches(filename,dirpath,index)
            if len(matches)==0:
                print("Missing:"+dirpath+"/"+filename)
            else:
                if len(list(filter(lambda filed: filed['name'] == filename,matches)))==0:
                    print("Renamed:"+dirpath+"/"+filename+"-->"+matches[0]['fullpath'])


index = generateLibraryRecords(sys.argv[2])
evaluateDirectory(sys.argv[1],index)

exit()
