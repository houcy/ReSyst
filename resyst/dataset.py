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
import random
import tempfile

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

    def split_by_percentage(self, _percentage):
        """
        Shortcut function for DataSet.split_by_count. This function
        will return 2 new datasets based on the current dataset.

        This function will calculate how many objects to be splitted
        in 2 new datasets based on the current count of objects. The
        function will then use DataSet.split_by_count to create the
        datasets.

        :param _percentage: A value between 0 and 1, representing the
        percentage of current objects to include in the first dataset.
        :return:  A tuple containing both datasets created.
        """
        assert _percentage > 0
        assert _percentage < 1

        count = len(self.objects) * _percentage
        return self.split_by_count(count)

    def split_by_count(self, _count):
        """
        Splits the current data set into 2 separated datasets.

        This function will first shuffle the internal directory
        to introduce randomness in the selection of items part of both
        datasets. Afterwards, the sets will be divided in 2; the first
        dataset will contain "_count" elements from the shuffled dictionary
        while the second dataset will contain the remaining items.

        This function will return a tuple containing the 2 datasets
        created.

        :param _count: The number of items to include in the first dataset.
        This value must be greater than 0 and lower than the count of items
        currently stored in the dataset object.

        :return: A tuple containing both datasets created.
        """
        assert _count > 0
        assert _count < len(self.objects)

        #
        # Reference:
        # https://stackoverflow.com/questions/19895028/randomly-shuffling-a-dictionary-in-python
        tkeys = list(self.objects.keys())
        tdict = {}
        random.shuffle(tkeys)

        for skey in tkeys:
            tdict[skey] = self.objects[skey]

        is1 = tdict.items()[_count:]
        is2 = tdict.items()[:_count]

        ds1 = DataSet(is1)
        ds2 = DataSet(is2)

        return ds1, ds2

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
            debug("{cf:d} file(s) found in '{sd:s}'.".format(
                cf = len(filenames),
                sd = _dir
            ))
            for filename in filenames:
                if _filter == None:
                    self.__add_file(os.path.join(root, filename))
                elif re.match(_filter, filename):
                    self.__add_file(os.path.join(root, filename))

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
                self.__add_file(_files)

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
        file_hash = new_file.hash()
        if file_hash not in self.objects.keys():
            self.objects[file_hash] = new_file
            debug("Added file: {f:s}.".format(
                f = str(new_file)
            ))
