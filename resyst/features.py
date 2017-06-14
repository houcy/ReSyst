#!/usr/bin/env python
# coding: utf-8
"""
    resyst.feature
    ~~~~~~~~~~~~~

    TODO: Description

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
import json
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
        assert _featureset is not None
        assert _destfile is not None

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
