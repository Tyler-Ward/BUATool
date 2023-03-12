#!/usr/bin/python3

import os
import sys
import filecmp
import hashlib
import click
from .util import calculateSHA1Sum, calculateMediaChecksum
from .index import DirectoryIndex


def findMatches(filename,index,features=[]):

    matches = []
    if "sha1" in features:
        filesha1 = calculateSHA1Sum(filename)
        if filesha1 == "da39a3ee5e6b4b0d3255bfef95601890afd80709":
            sha1=False

    if "media_checksum" in features:
        media_csum = calculateMediaChecksum(filename)
        if media_csum == None:
            media_checksum=False

    namematches = index.findFile(filename.split("/")[-1])
    for match in namematches:
        if "sha1" in features and filesha1 == match['sha1']:
            if filecmp.cmp(filename,index.directory_path + "/" + match['path']):
                matches.append(match)
        if not "sha1" in features:
            if filecmp.cmp(filename,index.directory_path + "/" + match['path']):
                matches.append(match)
    if len(matches)>0:
        return matches
    if "sha1" in features:
        hashmatches = index.findValue("sha1",filesha1)
        for match in hashmatches:
            if filecmp.cmp(filename,index.directory_path + "/" + match['path']):
                matches.append(match)
    if "media_checksum" in features:
        hashmatches = index.findValue("media_checksum",media_csum)
        for match in hashmatches:
                matches.append(match)



    return matches


def findFile(filename,index,features=[],delete=False):
    try:
        matches = findMatches(filename,index,features=features)
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



def evaluateDirectory(directory,index,features=[],delete=False):
    """Evaluates a directory an produces a result list"""
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            findFile(dirpath+"/"+filename,index,features=features,delete=delete)


@click.group()
def cli():
    """
    A tool to perform comparison on the contents of directories
    """
    pass


@cli.command()
@click.option('--sha1',default=False,is_flag=True,help="Compare files using their sha1sum as well as the name")
@click.option('--media_checksum',default=False,is_flag=True,help="Compare media files using the md5 of the contents")
@click.option('--rm',default=False,is_flag=True,help="automaticly delete matched files")
@click.option('--save-index',default=None,help="Location to save index to for later use")
@click.option('--load-index',default=None,help="Location to save index to for later use")
@click.argument('target')
@click.argument('reference')
def compare(target,reference,sha1,media_checksum,rm,load_index,save_index):
    """
    Compares two directories
    """

    features=[]

    if sha1:
        features.append("sha1")
    if media_checksum:
        features.append("media_checksum")


    reference_index = DirectoryIndex()
    if load_index != None:
        print("Loading Index from file")
        reference_index.loadIndex(load_index)
        for feature in features:
            if feature not in reference_index.features:
                print("Index is missing {} feature")
                exit()

        print("Index loaded")
    else:
        print("Indexing files on disk")
        reference_index.generateIndex(reference,features=features)
        print("Indexing generated")
    if save_index != None:
        reference_index.saveIndex(save_index)

    if os.path.isfile(target):
        print("checking single file")
        findFile(target,reference_index,features=features,delete=rm)
    else:
        evaluateDirectory(target,reference_index,features=features,delete=rm)

@cli.command()
@click.option('--sha1',default=False,is_flag=True,help="Compare files using their sha1sum as well as the name")
@click.option('--media_checksum',default=False,is_flag=True,help="Compare media files using the md5 of the contents")
@click.argument('target')
@click.argument('save_location')
def buildIndex(target,save_location,sha1,media_checksum):
    """
    Generates an index for a directory to allow for later use
    """


    features=[]
    if sha1:
        features.append("sha1")
    if media_checksum:
        features.append("media_checksum")

    index=DirectoryIndex()
    index.generateIndex(target,features=features)
    index.saveIndex(save_location)


@cli.command()
@click.argument('index')
def index_info(index):
    """
    Prints info about a pregenerated index
    """
    data_index = DirectoryIndex()
    data_index.loadIndex(index)

    print("Index info")
    print("==========")
    print("Path: " + data_index.directory_path)
    print("Date: " + data_index.indexed_on)
    print("File count: " + str(len(data_index.index)))

    print("Features:")
    for feature in data_index.features:
        print("  " + feature)


if __name__ == "__main__":
    cli()
    exit()
