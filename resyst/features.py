#!/usr/bin/env python
# coding: utf-8
"""
    resyst.feature
    ~~~~~~~~~~~~~

    TODO: Description

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
from enum import Enum

Feature = Enum(
    'BFD',
    'WFD',
    'BYTE_VAL_MEAN',
    'BYTE_VAL_STDDEV',
    'BYTE_VAL_MAD',
    'LOW_ASCII_FREQ',
    'HIGH_ASCII_FREQ',
    'STD_KURTOSIS',
    'STD_SKEWNESS',
    'AVG_BYTE_CONTINUITY',
    'LONGEST_STREAK',
    'SHANNON_ENTROPY'
)

class FeatureSet(object):
    @staticmethod
    def extract_features(_features, _codeblock):
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
        features = _features
        code_blocks = _codeblock

        if not isinstance(_features, list):
            features = [_features]

        return FeatureSet.__extract_features(features, code_blocks)

    @staticmethod
    def __extract_features(_features, _codeblock):
        """
        This is the internal standardize function to process calls to
        FeatureSet.extract_features.

        :param _features: A list of features to extract from the given
        code object.
        :param _codeblock: The CodeObject to extract features from.
        :return: A dictionary where the features are the keys and their
        values are the values associated to the feature.
        """
        features_data = {}

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
