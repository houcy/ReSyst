#!/usr/bin/env python
# coding: utf-8
"""
    resyst.dataset
    ~~~~~~~~~~~~~

    TODO: Description of module

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
import os
import re
import time
import shutil
import random
import tempfile
import threading

from resyst.log import *
from resyst.codeobject import FileObject

class DataSet(object):
    def __init__(self, _dict = None):
        if _dict == None:
            self.objects = {}
        else:
            assert isinstance(_dict, dict)
            self.objects = _dict

    def __len__(self):
        """
        Returns the number of objects in the dataset.
        :return: The number of objects in the dataset.
        """
        return len(self.objects)

    @property
    def data(self):
        """
        Returns a reference to the internal dictionary.
        :return: Reference to the internal dictionary.
        """
        return self.objects

class FileSet(DataSet):

    def __init__(self, _dict=None):
        super().__init__(_dict)

    def load_from_directory(self, _dir, _filter=None):
        """
        Creates a dataset of FileObject by reading all files within the
        given directory matching the provided filter.

        This function will recursively extract all files from the
        given directory. The list of files will then be matched with
        the given filter. By default, the filter will accept all files.
        Each filtered filename will be used to create a FileObject and
        stored into the DataSet object.

        :param _dir: The directory to traverse and list files from.
        :param _filter: A filter to exclude specific files. If none provided, allows
        all files.
        :return:
        """
        assert _dir is not None
        assert os.path.isdir(_dir)

        for root, dirs, filenames in os.walk(_dir):
            for filename in filenames:
                if _filter == None:
                    self.__add_file(os.path.join(root, filename))
                elif re.match(_filter, filename):
                    self.__add_file(os.path.join(root, filename))

    def add_directory(self, _directory, _filter=".*"):
        """
        Add files from the specified directory matching the
        given filter to the data set.

        This function will recursively traverse the given directory
        and extract all files from it. It will then add each file into
        the data set if they match the given filter given. If no filter is
        specified, then all files will be added by default.

        :param _directory: Directory containing files to add
        :param _filter: A regular expression specifying which files to include
        :return:
        """
        assert _directory is not None
        assert os.path.isdir(_directory)

        for root, dirs, files in os.walk(_directory):
            for file in files:
                if re.match(_filter, file):
                    self.__add_file(file)

    def add_file(self, _file):
        """
        Shortcut function for DataSet.add_files when only a single
        file needs to be added to the dataset.

        This function adds a single file to the dataset.

        :param _file: The absolute patht to a file to add to the dataset.
        :return:
        """
        self.add_files(_file)

    def add_files(self, _files):
        """
        Adds a list of files to the current dataset.

        This function will add a list containing absolute paths to files
        in the current dataset.

        :param _files: A list of absolute paths to files.
        :return:
        """
        assert _files is not None

        if isinstance(_files, list):
            for file in _files:
                if os.path.isfile(file):
                    self.__add_file(file)
        else:
            if os.path.isdir(_files):
                self.add_directory(_files)

    def __add_file(self, _file):
        """
        Adds a file to the dataset if it is not already currently
        referenced by it.

        This function will add the given file to the dataset unless is is
        already in the internal dictionary. To determine if the file is already
         in the data set, the files are stored internally within a dictionary
         object. A hash of the file, obtained via FileObject.hash(), is used as key.
         If the hash of the new file is already present in the dictionary, the file
         will not be added.

        :param _file: The absolute path of the file to add.
        :return: None
        """
        assert _file is not None
        assert os.path.isfile(_file)


        new_file = FileObject(_file)
        file_hash = new_file.hash
        if file_hash not in self.objects.keys():
            self.objects[file_hash] = new_file
            debug("Added file: {f:s}.".format(
                f = str(new_file)
            ))

