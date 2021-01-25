#!/usr/bin/python3

import os
import sys
import filecmp
import hashlib
import click
from util import calculateSHA1Sum
from index import DirectoryIndex


def findMatches(filename,filedir,index,sha1=False):

    matches = []
    if sha1:
        filesha1 = calculateSHA1Sum(filedir+"/"+filename)
        if filesha1 == "da39a3ee5e6b4b0d3255bfef95601890afd80709":
            sha1=False

    namematches = index.findFile(filename)
    for match in namematches:
        if sha1 and filesha1 == match['sha1']:
            if filecmp.cmp(filedir+"/"+filename,index.directory_path + "/" + match['path']):
                matches.append(match)
        if not sha1:
            if filecmp.cmp(filedir+"/"+filename,index.directory_path + "/" + match['path']):
                matches.append(match)
    if len(matches)>0:
        return matches
    if sha1:
        hashmatches = index.findHash(filesha1)
        for match in hashmatches:
            if filecmp.cmp(filedir+"/"+filename,index.directory_path + "/" + match['path']):
                matches.append(match)

    return matches




def evaluateDirectory(directory,index,sha1=False,delete=False):
    """Evaluates a directory an produces a result list"""

    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            try:
                matches = findMatches(filename,dirpath,index,sha1=sha1)
            except Exception as error:
                print("Issue evaluating checksum")
                print(error)
                continue
            try:
                if len(matches)==0:
                    print("Missing:"+dirpath+"/"+filename)
                else:
                    if len(list(filter(lambda filed: filed['name'] == filename,matches)))==0:
                        print("Renamed:"+dirpath+"/"+filename+"-->"+matches[0]['path'])
                    else:
                        print("Matched:"+dirpath+"/"+filename+"-->"+matches[0]['path'])
                    if delete:
                        print("Deleting: "+dirpath+"/"+filename)
                        os.remove(dirpath+"/"+filename);
            except Exception as error:
                print("Unable to process file")

@click.group()
def cli():
    pass


@cli.command()
@click.option('--sha1',default=False,is_flag=True,help="Compare files using their sha1sum as well as the name")
@click.option('--rm',default=False,is_flag=True,help="automaticly delete matched files")
@click.option('--save-index',default=None,help="Location to save index to for later use")
@click.option('--load-index',default=None,help="Location to save index to for later use")
@click.argument('target')
@click.argument('reference')
def buatool(target,reference,sha1,rm,load_index,save_index):

    reference_index = DirectoryIndex()

    if load_index != None:
        print("Loading Index from file")
        reference_index.loadIndex(load_index)
        print("Index loaded")
    else:
        print("Indexing files on disk")
        reference_index.generateIndex(reference,sha1=sha1)
    if save_index != None:
        reference_index.saveIndex(save_index)
    evaluateDirectory(target,reference_index,sha1=sha1,delete=rm)

@cli.command()
@click.option('--sha1',default=False,is_flag=True,help="Compare files using their sha1sum as well as the name")
@click.argument('target')
@click.argument('save_location')
def buildIndex(target,save_location,sha1):
    index=DirectoryIndex()
    index.generateIndex(target,sha1=sha1)
    index.saveIndex(save_location)



if __name__ == "__main__":
    cli()
    exit()
