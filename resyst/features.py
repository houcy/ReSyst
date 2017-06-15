#!/usr/bin/env python
# coding: utf-8
"""
    resyst.feature
    ~~~~~~~~~~~~~

    TODO: Description

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
import os
import json
import random
from enum import Enum
from resyst.dataset import DataSet

class Feature (Enum):
    BFD = 1
    WFD = 2
    BYTE_VAL_MEAN = 3
    BYTE_VAL_STDDEV = 4
    BYTE_VAL_MAD = 5
    LOW_ASCII_FREQ = 6
    HIGH_ASCII_FREQ = 7
    STD_KURTOSIS = 8
    STD_SKEWNESS = 9
    AVG_BYTE_CONTINUITY = 10
    LONGEST_STREAK = 11
    SHANNON_ENTROPY = 12

    def __str__(self):
        return self.name


class FeaturesEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Feature):
            return str(o)

class FeatureSet(object):

    @staticmethod
    def split_values_and_labels(_matrix):
        values_list = []
        labels_list = []
        for (values, labels) in _matrix:
            values_list.append(values)
            labels_list.append(labels)

        return values_list, labels_list

    @staticmethod
    def split_matrix(_matrix, _count):
        import random
        random.shuffle(_matrix)
        s1 = _matrix[:_count]
        s2 = _matrix[_count:]
        return s1, s2

    @staticmethod
    def serialize_features_matrix(_featureset, _order=None):
        assert _featureset is not None

        features_matrix = []

        for featuredict in _featureset:
            sfeat = FeatureSet.serialize_features_dict(featuredict)
            features_matrix.append(sfeat)

        return features_matrix

    @staticmethod
    def serialize_features_dict(_featuresdict, _order=None):
        assert _featuresdict is not None
        features_values = []
        features_labels = []

        feature_order = _order
        if feature_order is None:
            feature_order = _featuresdict.keys()

        for f in feature_order:
            if f in _featuresdict.keys() and f != "labels":
                v = _featuresdict[f]
                if isinstance(v, list):
                    features_values += v
                else:
                    features_values.append(v)

        if "labels" in _featuresdict.keys():
            features_labels = _featuresdict["labels"]

        return features_values, features_labels

    @staticmethod
    def extract_features_from_dataset(_features, _dataset):
        assert  _features is not None
        assert _dataset is not None
        assert len(_features) > 0
        assert len(_dataset) > 0
        assert isinstance(_dataset, DataSet)

        features_set = []

        for k in _dataset.data.keys():
            obj = _dataset.data[k]
            features_obj = FeatureSet.extract_features_from_single_object(_features, obj)
            features_set.append(features_obj)

        return features_set

    @staticmethod
    def extract_features_from_single_object(_features, _codeblock):
        """
        Extracts a given set of features from the given code and returns their
        values into a dictionary.

        This function will call the appropriate functions from the given
        code object based on the list of desired features. The list of
        features must contain values from the 'Feature' enumeration. The
        codeblock must be a CodeObject. This function will return a
        dictionary where the desired features are the keys and the
        computed values are the values.

        :param _features: A list of features to extract from the given
        code object.
        :param _codeblock: The CodeObject to extract features from.
        :return: A dictionary where the features are the keys and their
        values are the values associated to the feature.
        """
        assert  _features is not None
        assert _codeblock is not None
        assert len(_features) > 0

        features = _features
        code_blocks = _codeblock

        if not isinstance(_features, list):
            features = [_features]

        for f in features:
            assert isinstance(f, Feature)

        return FeatureSet.__extract_features_from_single_object(features, code_blocks)

    @staticmethod
    def save_features_to_json(_featureset, _destfile):
        """
        Saves a set of features to the provided destination file using the
        JSON format.

        This function will store the given feature set, which is expected to
        be a list of dictionaries created by the FeatureSet.extract_features_from_dataset
        function, to the given file using the JSON format.

        :param _featureset: A list of dictionaries
        :param _destfile: The JSON file to save the features into.
        :return:
        """
        assert _featureset is not None
        assert _destfile is not None

        #
        # Reference:
        # https://stackoverflow.com/questions/12734517/json-dumping-a-dict-gives-typeerror-keys-must-be-a-string
        for fdict in _featureset:
            for key in fdict.keys():
                if type(key) is not str:
                    try:
                        fdict[str(key)] = fdict[key]
                    except:
                        try:
                            fdict[repr(key)] = fdict[key]
                        except:
                            pass
                    del fdict[key]

        with open(_destfile, "w") as f:
            f.write(json.dumps(_featureset))

    @staticmethod
    def load_features_from_json(_jsonfile):
        """
        TODO
        :param _jsonfile:
        :return:
        """
        assert _jsonfile is not None
        assert os.path.isfile(_jsonfile)

        features_from_file = []

        with open(_jsonfile, "r") as f:
            json_data = json.load(f)

        # Replaces the keys with a Feature enum object
        for fdict in json_data:
            for skey in fdict.keys():
                if not isinstance(skey, Feature):
                    feature_value = fdict[skey]
                    if skey == Feature.BFD.name:
                        v = [0] * 256
                        for bvalue in feature_value.keys():
                            v[int(bvalue)] = int(feature_value[bvalue])
                        fdict[Feature[skey]] = v
                        del fdict[skey]
                    elif skey == Feature.WFD.name:
                        v = [0] * 65536
                        for bvalue in feature_value.keys():
                            v[int(bvalue)] = int(feature_value[bvalue])
                        fdict[Feature[skey]] = v
                        del fdict[skey]
                    elif skey == "labels":
                        #Single label for now:
                        fdict[skey] = feature_value[0]
                    else:
                        fdict[Feature[skey]] = float(feature_value)
                        del fdict[skey]

            features_from_file.append(fdict)

        return features_from_file

    @staticmethod
    def __extract_features_from_single_object(_features, _codeblock):
        """
        This is the internal standardize function to process calls to
        FeatureSet.extract_features.

        :param _features: A list of features to extract from the given
        code object.
        :param _codeblock: The CodeObject to extract features from.
        :return: A dictionary where the features are the keys and their
        values are the values associated to the feature.
        """
        features_data = {
            "labels"    :   _codeblock.labels
        }

        for ft in _features:
            if ft == Feature.BFD:
                features_data[Feature.BFD] = _codeblock.bfd()
            elif ft == Feature.WFD:
                features_data[Feature.WFD] = _codeblock.wfd()
            elif ft == Feature.BYTE_VAL_MEAN:
                features_data[Feature.BYTE_VAL_MEAN] = _codeblock.mean_byte_value()
            elif ft == Feature.BYTE_VAL_STDDEV:
                features_data[Feature.BYTE_VAL_STDDEV] = _codeblock.byte_std_dev()
            elif ft == Feature.BYTE_VAL_MAD:
                features_data[Feature.BYTE_VAL_STDDEV] = _codeblock.byte_mean_dev()
            elif ft == Feature.LOW_ASCII_FREQ:
                features_data[Feature.LOW_ASCII_FREQ] = _codeblock.low_ascii_freq()
            elif ft == Feature.HIGH_ASCII_FREQ:
                features_data[Feature.HIGH_ASCII_FREQ] = _codeblock.high_ascii_freq()
            elif ft == Feature.STD_KURTOSIS:
                features_data[Feature.STD_KURTOSIS] = _codeblock.byte_std_kurtosis()
            elif ft == Feature.STD_SKEWNESS:
                features_data[Feature.STD_SKEWNESS] = _codeblock.byte_mean_dev()
            elif ft == Feature.AVG_BYTE_CONTINUITY:
                features_data[Feature.AVG_BYTE_CONTINUITY] = _codeblock.byte_avg_continuity()
            elif ft == Feature.LONGEST_STREAK:
                features_data[Feature.LONGEST_STREAK] = _codeblock.longest_byte_streak()
            elif ft == Feature.SHANNON_ENTROPY:
                features_data[Feature.SHANNON_ENTROPY] = _codeblock.shannon_entropy()

        return features_data


class FeatureData(object):
    def __init__(self, _data = None):
        self._data = _data

    def __len__(self):
        return len(self._data)

    @property
    def data(self): return self._data

    def get_training_and_test_sets(self, _percentage):
        assert _percentage > 0
        assert _percentage < 1

        ds1, ds2 = self.__split_by_percentage(_percentage)

        ds1_values, ds1_labels = ds1.__serialize_features_matrix()
        ds2_values, ds2_labels = ds1.__serialize_features_matrix()

        return [(ds1_values, ds1_labels), (ds2_values, ds2_labels)]

    def __split_by_percentage(self, _percentage):
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

        count = int(len(self._data) * _percentage)
        return self.__split_by_count(count)

    def __split_by_count(self, _count):
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
        assert _count < len(self._data)

        random.shuffle(self._data)

        is1 = self._data[_count:]
        is2 = self._data[:_count]

        ds1 = FeatureData(is1)
        ds2 = FeatureData(is2)

        return ds1, ds2

    def __serialize_features_matrix(self):

        features_values = []
        features_labels = []

        for featuredict in self._data:
            v, l = FeatureSet.serialize_features_dict(featuredict)
            features_values.append(v)
            features_labels.append(l)

        return features_values, features_labels

    def __serialize_features_dict(self, _featuresdict):
        assert _featuresdict is not None
        features_values = []
        features_labels = []

        for f in _featuresdict.keys():
            if f in _featuresdict.keys() and f != "labels":
                v = _featuresdict[f]
                if isinstance(v, list):
                    features_values += v
                else:
                    features_values.append(v)

        if "labels" in _featuresdict.keys():
            features_labels = _featuresdict["labels"]

        return features_values, features_labels

    @staticmethod
    def load_features_from_json(_jsonfile):
        """
        TODO
        :param _jsonfile:
        :return:
        """
        assert _jsonfile is not None
        assert os.path.isfile(_jsonfile)

        features_from_file = []

        with open(_jsonfile, "r") as f:
            json_data = json.load(f)

        # Replaces the keys with a Feature enum object
        for fdict in json_data:
            labels = None
            for skey in fdict.keys():
                if not isinstance(skey, Feature):
                    feature_value = fdict[skey]
                    if skey == Feature.BFD.name:
                        v = [0] * 256
                        for bvalue in feature_value.keys():
                            v[int(bvalue)] = int(feature_value[bvalue])
                        fdict[Feature[skey]] = v
                        del fdict[skey]
                    elif skey == Feature.WFD.name:
                        v = [0] * 65536
                        for bvalue in feature_value.keys():
                            v[int(bvalue)] = int(feature_value[bvalue])
                        fdict[Feature[skey]] = v
                        del fdict[skey]
                    elif skey == "labels":
                        # Single label for now:
                        fdict[skey] = feature_value[0]
                    else:
                        fdict[Feature[skey]] = float(feature_value)
                        del fdict[skey]

            features_from_file.append(fdict)

        fd = FeatureData(features_from_file)
        return fd
