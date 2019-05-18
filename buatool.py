#!/usr/bin/python3

import os
import sys
import filecmp
import hashlib
import click


def calculateSHA1Sum(filename):
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def generateLibraryRecords(directory,sha1=False):
    """Create a library record for a target directory"""

    fileindex=[]

    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            try:
                filedetails={
                        'name':filename,
                        'folder':dirpath,
                        'fullpath':dirpath+"/"+filename,
                        }
                if sha1:
                    filedetails['sha1']=calculateSHA1Sum(dirpath+"/"+filename)
                fileindex.append(filedetails)
            except (FileNotFoundError,PermissionError):
                print("Unable to index "+dirpath+"/"+filename)
    return fileindex


def findFile(name,index):
    return(list(filter(lambda filed: filed['name'] == name,index)))

def findHash(sha1,index):
    return(list(filter(lambda filed: filed['sha1'] == sha1,index)))

def findMatches(filename,filedir,index,sha1=False):

    matches = []
    filesha1 = calculateSHA1Sum(filedir+"/"+filename)

    namematches = findFile(filename,index)
    for match in namematches:
        if sha1 and filesha1 == match['sha1']:
            if filecmp.cmp(filedir+"/"+filename,match['fullpath']):
                matches.append(match)
    if len(matches)>0:
        return matches
    if sha1:
        hashmatches = findHash(filesha1,index)
        for match in hashmatches:
            if filecmp.cmp(filedir+"/"+filename,match['fullpath']):
                matches.append(match)

    return matches




def evaluateDirectory(directory,index,sha1=False):
    """Evaluates a directory an produces a result list"""

    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            matches = findMatches(filename,dirpath,index,sha1=sha1)
            if len(matches)==0:
                print("Missing:"+dirpath+"/"+filename)
            else:
                if len(list(filter(lambda filed: filed['name'] == filename,matches)))==0:
                    print("Renamed:"+dirpath+"/"+filename+"-->"+matches[0]['fullpath'])

def saveIndex(index,location):
    import json
    with open(location,"w") as output:
        json.dump(index,output)

def loadIndex(location):
    import json
    with open(location,"r") as indexInput:
        return(json.load(indexInput))


@click.command()
@click.option('--sha1',default=False,is_flag=True,help="Compare files using their sha1sum as well as the name")
@click.option('--save-index',default=None,help="Location to save index to for later use")
@click.option('--load-index',default=None,help="Location to save index to for later use")
@click.argument('target')
@click.argument('reference')
def buatool(target,reference,sha1,load_index,save_index):

    if load_index != None:
        index = loadIndex(load_index)
    else:
        index = generateLibraryRecords(reference,sha1=sha1)
    if save_index != None:
        saveIndex(index,save_index)
    evaluateDirectory(target,index,sha1=sha1)


if __name__ == "__main__":
    buatool()
    exit()
