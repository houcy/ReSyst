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
import tempfile
from resyst.codeobject import FileObject

class DataSet(object):
    def __init__(self):
        self.objects = {}

    def load_from_directory(self, _dir, _filter=".*"):
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
                if re.match(filename, _filter):
                    new_file = FileObject(filename)
                    file_hash = new_file.hash()
                    if file_hash not in self.objects:
                        self.objects[file_hash] = new_file
