#!/usr/bin/python3

import os
import filecmp
import click
from .index import DirectoryIndex
from .plugin_helper import discovered_plugins, get_plugin


def findMatches(filename, index, plugins=[]):

    matches = []

    namematches = index.findFile(filename.split("/")[-1])
    for match in namematches:
        if filecmp.cmp(filename, index.directory_path + "/" + match['path']):
            matches.append(("Matched", match))
    if len(matches) > 0:
        return matches

    for plugin in plugins:
        matches.extend(plugin.findMatches(filename, index))

    return matches


def findFile(filename, index, plugins=[], delete=False):
    try:
        matches = findMatches(filename, index, plugins=plugins)
    except Exception as error:
        print("Issue evaluating checksum")
        print(error)
        return
    try:
        if len(matches) == 0:
            print("Missing:"+filename)
        else:
            print(matches[0][0]+":"+filename+"-->"+matches[0][1]['path'])
            if delete:
                print("Deleting: "+filename)
                os.remove(filename)
    except Exception:
        print("Unable to process file")


def evaluateDirectory(directory, index, plugins=[], delete=False):
    """Evaluates a directory an produces a result list"""
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            findFile(dirpath+"/"+filename, index, plugins=plugins, delete=delete)

def getPlugins(plugin_names):
    if plugin_names:
        plugins = []
        for plugin_name in plugins:
            found_plugin = get_plugin(plugin_name)
            if found_plugin is None:
                print("unable to load plugin {}".format(plugin_name))
                exit(1)
            plugins.append(found_plugin)

    else:
        plugins = discovered_plugins
    return plugins


@click.group()
def cli():
    """
    A tool to perform comparison on the contents of directories
    """
    pass


@cli.command()
@click.option('--rm', default=False, is_flag=True, help="automaticly delete matched files")
@click.option('--save-index', default=None, help="Location to save index to for later use")
@click.option('--load-index', default=None, help="Location to save index to for later use")
@click.option('--plugin', '-p', "plugin_names", multiple=True, help="specify plugin to use, , default is to use all plugins")
@click.argument('target')
@click.argument('reference')
def compare(target, reference, plugin_names, rm, load_index, save_index):
    """
    Compares two directories
    """

    plugins = getPlugins(plugin_names)

    reference_index = DirectoryIndex()
    if load_index is not None:
        print("Loading Index from file")
        reference_index.loadIndex(load_index)
        for plugin in plugins:
            if plugin.name not in reference_index.features:
                print("Index is missing {} feature")
                exit()

        print("Index loaded")
    else:
        print("Indexing files on disk")
        reference_index.generateIndex(reference, plugins=plugins)
        print("Indexing generated")
    if save_index is not None:
        reference_index.saveIndex(save_index)

    if os.path.isfile(target):
        print("checking single file")
        findFile(target, reference_index, plugins=plugins, delete=rm)
    else:
        evaluateDirectory(target, reference_index, plugins=plugins, delete=rm)


@cli.command()
@click.option('--plugin', '-p', "plugin_names", multiple=True, help="specify plugin to use, , default is to use all plugins")
@click.argument('target')
@click.argument('save_location')
def buildIndex(target, save_location, plugin_names):
    """
    Generates an index for a directory to allow for later use
    """

    plugins = getPlugins(plugin_names)

    index = DirectoryIndex()
    index.generateIndex(target, plugins=plugins)
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

@cli.command()
@click.argument('plugin_name', default="")
def pluggin_info(plugin_name=""):
    if plugin_name == "":
        print("Detected plugins")
        print("==========")

        for plugin in discovered_plugins:
            print(plugin.name)
    else:
        selected_plugin = get_plugin(plugin_name)

        if selected_plugin is None:
            print("unable to find plugin {}".format(plugin_name))
            exit(1)

        print(selected_plugin.__doc__)

if __name__ == "__main__":
    cli()
    exit()
