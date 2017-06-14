#!/usr/bin/env python
# coding: utf-8
"""
    resyst.codeobject
    ~~~~~~~~~~~~~

    Todo: description of module

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""

import os
import math
import struct
import hashlib

from resyst.log import *

class LabelledObject(object):
    def __init__(self, _labels = None):
        """
        Initializes the object with the given labels if any.
        :param _labels: A list of label to add to the object.
        """
        if _labels == None:
            self.__labels = []
        else:
            self.__labels = _labels

    def __str__(self):
        """
        Returns a comma-separated string of the labels.
        :return: A comma-separated string of the labels.
        """
        return ','.join(self.__labels)

    @property
    def labels(self):
        """
        Returns the list of labels associated with this object.
        :return: The list of labels associated with this object.
        """
        return self.__labels

    def add_label(self, _label):
        """
        Adds a label to the current object if not already in the
        internal list.
        :param _label: The label to add. Cannot be 'None'
        :return:
        """
        assert _label != None
        if _label not in self.__labels:
            debug("Adding label '{l:s}' to object '{os:s}'.".format(
                l = _label, os = str(self)
            ))
            self.__labels.append(_label)

class CodeObject(LabelledObject):
    def __init__(self, _binarydata):
        assert _binarydata is not None
        super().__init__()

        self._data = _binarydata

    def __str__(self):
        fmt = "<CodeObject Size={s:d} byte(s), MD5={h:s}>"
        return fmt.format(s=len(self._data), h=self.md5())

    def __len__(self):
        """
        Returns the length of the binary object.
        """
        return len(self._data)

    def __eq__(self, _other):
        """
        Verifies if this object is equal to the object provided.

        To be equivalent, the object provided must be:
        1) A CodeObject; and
        2) Contain the same binary data.

        @param _other The object to compare with
        @return True if the other object is a BinaryObject containing the same
        data.
        """
        if isinstance(_other, self.__class__):
            return self._data == _other.__data
        return False

    def __ne__(self, _other):
        """
        Verifies if this object is unequal to the object provided.

        To be equivalent, the object provided must be:
        1) A CodeObject; and
        2) Contain the same binary data.

        @param _other The object to compare with
        @return True if the other object is a not BinaryObject or does not contain
        the same data.
        """
        return not self.__eq__(_other)

    @staticmethod
    def from_file(_file, _mode="rb"):
        """
        Generates a CodeObject from the contents of the given file.

        @param _file The file to read the contents from.
        @param _mode The mode to read the file. By default the mode is "rb"
        @return A CodeObject loaded with the contents of the given file.
        """
        assert _file is not None
        assert os.path.isfile(_file)

        with open(_file, _mode) as f:
            data = f.read()

        return CodeObject(data)

    def get_data(self):
        """
        Returns the data currently held by this object.

        @return Data contained in this object.
        """
        return self._data

    def split_by_size(self, _chunksize):
        """
        Splits the current CodeObject into multiple smaller code objects.

        This function will return a generator containing a the current
        code object divided into multiple chunks of the specified size.

        @param _chunksize The size, in bytes of the chunks
        @return A generator containing the chunks of data.

        Reference:
            https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        """
        assert _chunksize < len(self._data)

        for i in range(0, len(self._data), _chunksize):
            yield CodeObject(self._data[i:i + _chunksize])

    def to_file(self, _file, _mode="wb"):
        """
        Dumps the contents of the current object into the specified file.

        @param _file The destination file.
        @param _mode The writing mode. By default the mode is "wb"
        """
        assert len(self._data) > 0
        assert _file is not None

        with open(_file, _mode) as f:
            f.write(self._data)

    def bfd(self):
        """
        Calculates the byte frequency distribution of the current
        binary object.

        This function will iterate through each byte within the
        current data and create a dictionary in which the byte will be
        the key and the frequency of the byte, its associated value.
        For example, consider the following dictionary:

        { 0x01 : 30, 0x30 : 1, 0x46 : 5, 0xFF : 32 }

        The dictionary above indicates that byte 1 appears 30 times, byte 0x30 appears
        once etc...

        @return A dictionary containing the frequency of each byte within the
        current binary object.
        """
        dist = {}
        for b in self._data:
            if b in dist:
                dist[b] += 1
            else:
                dist[b] = 1
        return dist

    def wfd(self):
        """
        Calculates the word frequency distribution of the current
        binary object.

        This function is similar to bfd(), but uses word-sized
        elements rather than bytes. The results will be stored in a dictionary
        in which the words are the keys, and their frequencies are the values.

        @return A dictionary containing the frequency of each wprd within the
        current binary object.
        """
        dist = {}
        for i in range(0, len(self._data), 2):
            w = struct.unpack("H", self._data[i:i + 1])[0]
            if w in dist:
                dist[w] += 1
            else:
                dist[w] = 1

        return dist

    def mean_byte_value(self):
        """
        Calculates the mean byte value of the code object.

        This function will iterate through each byte of the object
        and calculate the arithmetic mean of all bytes within the
        contents of the object.

        @return The mean value of all bytes within the object.
        """
        return sum(map(ord, self._data)) / len(self._data)

    def byte_std_dev(self):
        """
        Calculates the standard deviation of the byte values contained
        in the code object.

        @return The standard deviation of the byte values within the
        contents of the object.
        """
        x_i = self.mean_byte_value()
        s_i = math.sqrt(sum([math.pow(x - x_i, 2) for x in map(ord, self._data)]) / (len(self._data) - 1))
        return s_i

    def byte_mean_dev(self):
        """
        Calculates the mean absolute deviation (MAD) of the byte values
        contained in the code object.

        @return The mean absolute deviation (MAD) of the byte values within
        the contents of the object.
        """
        x_i = self.mean_byte_value()
        mad = sum([abs(x - x_i) for x in map(ord, self._data)]) / (len(self._data))
        return mad

    def byte_std_kurtosis(self):
        """
        Calculates the standard kurtosis of the bytes contained within the object.

        @return The standard kurtosis value of the bytes within the current object.

        References:
            https://en.wikipedia.org/wiki/Kurtosis
        """
        x_i = self.mean_byte_value()
        s_i = self.byte_std_dev()
        k_i = sum([math.pow(x - x_i, 4) for x in map(ord, self._data)]) / (
            (len(self._data) - 1) * math.pow(s_i, 4))
        return k_i

    def byte_std_skewness(self):
        """
        Calculates the standard skewness of the bytes value distribution.

        @return The standard skewness value of the bytes within the current object.

        References:

        """
        x_i = self.mean_byte_value()
        s_i = self.byte_std_dev()
        g_i = sum([math.pow(x - x_i, 3) for x in map(ord, self._data)]) / (
            (len(self._data) - 1) * math.pow(s_i, 3))
        return g_i

    def byte_avg_continuity(self):
        """
        Calculates the average distance between consecutive the bytes of this object.

        @return Average distance between consecutive bytes.
        """
        x_i = self.mean_byte_value()
        b_v = map(ord, self._data)
        d = sum([math.pow(x - x_i, 4) for x in b_v])
        t = math.pow(sum([math.pow(x - x_i, 2) for x in b_v]), 2)
        c_i = len(self._data) * (d / t)
        return c_i

    def longest_byte_streak(self):
        """
        Locates the longest streak of the same byte within the contents
        of the object.

        This function will iterate over each byte of the object and
        find the byte with the longest consecutive repetition. For example
        if the content of the object is the following:

        "AABB12CCCC"

        This function will return a tuple with the following values: ("C", 4)

        @return A tuple containing the value of the byte and the size
        of its longest consecutive streak.
        """
        i = 0
        n = len(self._data)
        max_byte = self._data[0]
        max_streak = 1

        while (i + 1) < n:
            cur_streak = 0
            while ((i + 1) < n) and (self._data[i] == self._data[i + 1]):
                cur_streak += 1
                i += 1
            if cur_streak > max_streak:
                max_byte = self._data[i]
                max_streak = cur_streak
            i += 1
        return max_byte, max_streak

    def low_ascii_freq(self):
        """
        Returns the frequencies of the lower ASCII characters, i.e. characters
        with ASCII codes between 32 and 127.

        This function will use the bdf() function and will then return the
        subset containing only bytes within the lower ASCII range. This function
        returns a dictionary with characters as keys and their frequency as
        value.

        @return A dictionary containing the ASCII character as key and its
        frequency as value.
        """
        f = self.__bfd_subrange(_min=32, _max=127)

        # Replaces ascii codes with corresponding characters
        for b in f.keys():
            f[chr(b)] = f[b]
            del f[b]
        return f

    def high_ascii_freq(self):
        """
        Returns the frequencies of the higher ASCII characters, i.e. characters
        with ASCII codes between 128 and 255.

        This function will use the bdf() function and will then return the
        subset containing only bytes within the higher ASCII range. This function
        returns a dictionary with characters as keys and their frequency as
        value.

        @return A dictionary containing the ASCII character as key and its
        frequency as value.
        """
        f = self.__bfd_subrange(_min=128, _max=255)
        # Replaces ascii codes with corresponding characters
        for b in f.keys():
            f[chr(b)] = f[b]
            del f[ord(b)]

        return f

    def shannon_entropy(self):
        """
        Calculates the Shannon entropy of the current code object.

        @return The entropy of the current object.
        """
        entropy = 0
        for b in self._data:
            p_x = float(self._data.count(b)) / len(self._data)
            if p_x > 0.0:
                entropy += p_x * math.log(p_x, 2)
        return entropy

    def md5(self):
        """
        Returns a string hexadecimal representation of the MD5 digest of the
        data contained in this object.

        @return A string containing the hexadecimal representation of the
        MD5 of the contents of this object.
        """
        m = hashlib.md5()
        d = self._data
        if isinstance(d, bytes):
            m.update(d)
        else:
            m.update(d.encode("utf-8"))
        return m.hexdigest()

    def sha1(self):
        """
        Returns a string hexadecimal representation of the SHA1 digest of the
        data contained in this object.

        @return A string containing the hexadecimal representation of the
        SHA1 of the contents of this object.
        """
        m = hashlib.sha1()
        d = self._data
        if isinstance(d, bytes):
            m.update(d)
        else:
            m.update(d.encode("utf-8"))
        return m.hexdigest()

    def sha224(self):
        """
        Returns a string hexadecimal representation of the SHA224 digest of the
        data contained in this object.

        @return A string containing the hexadecimal representation of the
        SHA224 of the contents of this object.
        """
        m = hashlib.sha224()
        d = self._data
        if isinstance(d, bytes):
            m.update(d)
        else:
            m.update(d.encode("utf-8"))
        return m.hexdigest()

    def sha256(self):
        """
        Returns a string hexadecimal representation of the SHA256 digest of the
        data contained in this object.

        @return A string containing the hexadecimal representation of the
        SHA256 of the contents of this object.
        """
        m = hashlib.sha256()
        d = self._data
        if isinstance(d, bytes):
            m.update(d)
        else:
            m.update(d.encode("utf-8"))
        return m.hexdigest()

    def sha384(self):
        """
        Returns a string hexadecimal representation of the SHA384 digest of the
        data contained in this object.

        @return A string containing the hexadecimal representation of the
        SHA384 of the contents of this object.
        """
        m = hashlib.sha384()
        d = self._data
        if isinstance(d, bytes):
            m.update(d)
        else:
            m.update(d.encode("utf-8"))
        return m.hexdigest()

    def sha512(self):
        """
        Returns a string hexadecimal representation of the SHA512 digest of the
        data contained in this object.

        @return A string containing the hexadecimal representation of the
        SHA512 of the contents of this object.
        """
        m = hashlib.sha512()
        d = self._data
        if isinstance(d, bytes):
            m.update(d)
        else:
            m.update(d.encode("utf-8"))
        return m.hexdigest()

    def __bfd_subrange(self, _min, _max, _exclude=[]):
        """
        Returns a specific subset of the BFD.

        This function will calculate the BFD of the object using the bfd()
        function and then select only the specified bytes from the resulting
        dictionary. The function will return a dictionary with only the
        selected bytes.

        @param _min Smallest byte value to select. Must be greater than 0.
        @param _max Largest byte value to select. Must be lower than 255.
        @param _exclude Bytes to exclude within the given range.
        @return A dictionary containing the bytes as keys and their corresponding
        frequencies as values.
        """
        assert _min > 0
        assert _max < 255

        bfd = self.bfd()
        sub_bfd = {}
        for i in range(_min, _max):
            if i not in _exclude and i in bfd:
                sub_bfd[i] = bfd[i]
        return sub_bfd

    def __wfd_subrange(self, _min, _max, _exclude=[]):
        """
        Returns a specific subset of the WFD.

        This function will calculate the WFD of the object using the bfd()
        function and then select only the specified bytes from the resulting
        dictionary. The function will return a dictionary with only the
        selected bytes.

        @param _min Smallest byte value to select. Must be greater than 0.
        @param _max Largest byte value to select. Must be lower than 65535.
        @param _exclude Words to exclude within the given range.
        @return A dictionary containing the bytes as keys and their corresponding
        frequencies as values.
        """
        assert _min > 0
        assert _max < 65535

        bfd = self.wfd()
        sub_bfd = {}
        for i in range(_min, _max):
            if i not in _exclude and i in bfd:
                sub_bfd[i] = bfd[i]
        return sub_bfd


class FileObject(CodeObject):
    def __init__(self, _file):
        """
        Creates a FileObject by initializing the parent class, CodeObject,
        with the contents of the given file.
        :param _file: The file to retrieve contents from.
        """
        assert _file is not None
        assert os.path.exists(_file)

        super().__init__('')
        self.filename = _file
        with open(_file, "rb") as f:
            self._data = f.read()

    def __str__(self):
        fmt = "<FileObject Size={fs:d} byte(s) Hash='{fh:s}'>"
        return fmt.format(
            fs = len(self._data), fh = self.hash()
        )

    def hash(self):
        """
        Returns the SHA224 hash of the file.
        :return: Returns the SHA224 hash of the file.
        """
        return self.sha224()

    @property
    def file_path(self):
        """
        Returns the path of this file object.
        :return: the path of this file object.
        """
        return self.filename

    @property
    def extension(self):
        """
        Returns the extension of the file if any.

        This function will return the file extension based
        on the position of the "." in the file name. If no dot
        is found, returns an empty string.

        :return: The extension of the file, or an empty string if none
        found.
        """
        if "." in self.filename:
            return os.path.splitext(self.filename)[1][1:].upper()
        else:
            return ""

    def set_extension_as_label(self):
        """
        Adds the file extension as a label of the file object.
        :return:
        """
        self.add_label(self.extension)
