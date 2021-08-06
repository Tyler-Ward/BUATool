#!/usr/bin/python3

import os
import sys
import filecmp
import hashlib
import click
from .util import calculateSHA1Sum
from .index import DirectoryIndex


def findMatches(filename,index,sha1=False):

    matches = []
    if sha1:
        filesha1 = calculateSHA1Sum(filename)
        if filesha1 == "da39a3ee5e6b4b0d3255bfef95601890afd80709":
            sha1=False

    namematches = index.findFile(filename.split("/")[-1])
    for match in namematches:
        if sha1 and filesha1 == match['sha1']:
            if filecmp.cmp(filename,index.directory_path + "/" + match['path']):
                matches.append(match)
        if not sha1:
            if filecmp.cmp(filename,index.directory_path + "/" + match['path']):
                matches.append(match)
    if len(matches)>0:
        return matches
    if sha1:
        hashmatches = index.findHash(filesha1)
        for match in hashmatches:
            if filecmp.cmp(filename,index.directory_path + "/" + match['path']):
                matches.append(match)

    return matches


def findFile(filename,index,sha1=False,delete=False):
    try:
        matches = findMatches(filename,index,sha1=sha1)
    except Exception as error:
        print("Issue evaluating checksum")
        print(error)
        return
    try:
        if len(matches)==0:
            print("Missing:"+filename)
        else:
            if len(list(filter(lambda filed: filed['name'] == filename,matches)))==0:
                print("Renamed:"+filename+"-->"+matches[0]['path'])
            else:
                print("Matched:"+filename+"-->"+matches[0]['path'])
            if delete:
                print("Deleting: "+filename)
                os.remove(filename);
    except Exception as error:
        print("Unable to process file")



def evaluateDirectory(directory,index,sha1=False,delete=False):
    """Evaluates a directory an produces a result list"""
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            findFile(dirpath+"/"+filename,index,sha1=sha1,delete=delete)


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
        if sha1:
            if not "sha1" in reference_index.features:
                print("Index missing checksums, Update index or run without checksums")
                exit(1)
        print("Index loaded")
    else:
        print("Indexing files on disk")
        reference_index.generateIndex(reference,sha1=sha1)
    if save_index != None:
        reference_index.saveIndex(save_index)

    if os.path.isfile(target):
        print("checking single file")
        findFile(target,reference_index,sha1=sha1,delete=rm)
    else:
        evaluateDirectory(target,reference_index,sha1=sha1,delete=rm)

@cli.command()
@click.option('--sha1',default=False,is_flag=True,help="Compare files using their sha1sum as well as the name")
@click.argument('target')
@click.argument('save_location')
def buildIndex(target,save_location,sha1):
    index=DirectoryIndex()
    index.generateIndex(target,sha1=sha1)
    index.saveIndex(save_location)


@cli.command()
@click.argument('index')
def index_info(index):
    data_index = DirectoryIndex()
    data_index.loadIndex(index)

    print("Index info")
    print("Path: " + data_index.directory_path)
    print("Date: " + data_index.indexed_on)
    print("File count: " + str(len(data_index.index)))


if __name__ == "__main__":
    cli()
    exit()
