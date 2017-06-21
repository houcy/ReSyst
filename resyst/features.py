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
import time
import random
import threading
from enum import Enum

from resyst.codeobject import *
from sklearn.preprocessing import normalize

class Feature(Enum):
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
    LABEL = 13

    def __str__(self):
        return self.name


class FeatureSet(object):
    __extracting = False

    @staticmethod
    def extract_features_from_fileset(_features, _fileset):
        """
        Extract one or multiple features from all files contained in the given
        file set.

        This function will iterate thru each FileObject within the
        given file set and extract each feature required. This function
        will return a dictionary of dictionaries:

        results = {
          <FileObject1.hash> : {
                <Feature1>   :   <Value1(s)>,
                <Feature2>   :   <Value2(s)>
                ...
                }
        }

        :param _features: A list of Feature objects.
        :param _fileset: A FileSet object with one or more FileObject
        :return: A dictionary of features in which the keys are the hash of the
        file object and the values are dictionaries of features, including the
        labels.
        """
        assert _features is not None
        assert _fileset is not None
        assert len(_features) > 0
        assert len(_fileset) > 0
        from queue import Queue

        extracted_features_queue = Queue()
        extracted_features_dict = {}
        FeatureSet.__extracting = True

        threads = []
        process_features_from_queue = threading.Thread(
            name="t_extracted_features_queue_reader",
            target=FeatureSet.__manage_extracted_feature_queue,
            args=(extracted_features_queue, extracted_features_dict)
        )

        process_features_from_queue.start()

        files = _fileset.objects.values()
        for file in files:
            for feature in _features:
                t = threading.Thread(
                    name="t_{f:s}_{h:s}".format(f=feature, h=file.hash),
                    target=FeatureSet.__extract_feature_from_code_object,
                    args=(feature, file, extracted_features_queue)
                )
                while len(threads) >= 30:
                    time.sleep(0.8)
                    for st in threads:
                        if not st.is_alive():
                            threads.remove(st)

                threads.append(t)
                t.start()
            time.sleep(0.3)

        debug("Waiting for feature extraction threads to terminate ({tc:d})...".format(
            tc=len(threads)
        ))
        time.sleep(2)
        t_i = 0
        while len(threads) > 0:
            t = threads[t_i % len(threads)]
            t.join(timeout=2)
            if t.is_alive():
                debug("\tWaiting on '{tn:s}'...".format(tn=t.name))
            else:
                threads.remove(t)
            t_i += 1
            time.sleep(2)

        FeatureSet.__extracting = False

        process_features_from_queue.join(timeout=3)
        if process_features_from_queue.is_alive():
            warn("Failed to terminate thread '{tn:s}'.".format(tn=process_features_from_queue.name))

        features_data = FeatureData(extracted_features_dict)
        return features_data

    @staticmethod
    def __extract_feature_from_code_object(_feature, _code, _queue):
        """
        Extracts a specific feature from the given code object and adds the extracted
        information in the provided queue.

        This function will verify the given feature and call the associated function of
        the code object. It will store the code object, the Feature object and the
        results into a tuple, which will be enqueued for later retrieval. The tuple
        enqueue is in the format (_code, _feature, results).

        :param _feature: The feature to extract. Must be a Feature enum.
        :param _code: The code object to extract the feature from. Must be a CodeObject.
        :param _queue: A Queue object in which the data will be enqueued.
        :return:
        """
        assert _feature is not None
        assert _code is not None and isinstance(_code, CodeObject)
        assert _queue is not None
        debug("Extracting '{fn:s}' from code object '{h:s}'...".format(
            fn=_feature, h=_code.hash
        ))
        feature_data = None

        if _feature == Feature.BFD:
            feature_data = _code.bfd()
        elif _feature == Feature.WFD:
            feature_data = _code.wfd()
        elif _feature == Feature.BYTE_VAL_MEAN:
            feature_data = _code.mean_byte_value()
        elif _feature == Feature.BYTE_VAL_STDDEV:
            feature_data = _code.byte_std_dev()
        elif _feature == Feature.BYTE_VAL_MAD:
            feature_data = _code.byte_mean_dev()
        elif _feature == Feature.LOW_ASCII_FREQ:
            feature_data = _code.low_ascii_freq()
        elif _feature == Feature.HIGH_ASCII_FREQ:
            feature_data = _code.high_ascii_freq()
        elif _feature == Feature.STD_KURTOSIS:
            feature_data = _code.byte_std_kurtosis()
        elif _feature == Feature.STD_SKEWNESS:
            feature_data = _code.byte_mean_dev()
        elif _feature == Feature.AVG_BYTE_CONTINUITY:
            feature_data = _code.byte_avg_continuity()
        elif _feature == Feature.LONGEST_STREAK:
            feature_data = _code.longest_byte_streak()
        elif _feature == Feature.SHANNON_ENTROPY:
            feature_data = _code.shannon_entropy()

        _queue.put((_code, _feature, feature_data))

    @staticmethod
    def __manage_extracted_feature_queue(_queue, _features_dict):
        """
        Consumes the objects contained in the given queue and inserts them
        in the dictionary object provided.

        This function expects a tuple of 3 items to be rad from the Queue. The first
        item should be a FileObject, the second should be a Feature enumeration and
        the third one, the value for that Feature extracted from the FileObject:
        (<FileObject>, <Feature>, feature_result)

        The values of this tuple will be inserted into the given dictionary. The
        dictionary created by this function is in the following format:

        {
          <FileObject1.hash>     :   {  <Feature1>    :  <Value1>,
                                        ...
                                        <FeatureN>    :  <ValueN>,
          ...
        }

        :param _queue: A queue.Queue object from which object will be consumed.
        :param _features_dict: A dictionary object containing the features extracted
        from file objects.
        :return:
        """
        while FeatureSet.__extracting:
            (fobj, feature, feature_result) = _queue.get()
            if fobj.hash in _features_dict:
                _features_dict[fobj.hash][feature] = feature_result
                debug("Added feature '{:s}' to '{:s}'.".format(feature, fobj.hash))
            else:
                _features_dict[fobj.hash] = {
                    feature: feature_result,
                    Feature.LABEL: fobj.labels
                }
            _queue.task_done()
            time.sleep(0.5)


class FeatureData(object):
    def __init__(self, _data=None):
        self._data = _data

    def __len__(self):
        return len(self._data)

    @property
    def data(self):
        return self._data

    def to_feature_matrix(self):

        feature_matrix = []
        feature_labels = []

        for fdict in self._data:
            feature_vector = []
            for skey in fdict.keys():
                feature_value = fdict[skey]
                if skey == Feature.LABEL:
                        # Single label for now:
                        feature_labels.append(feature_value)
                else:
                    if isinstance(feature_value, list):
                        feature_vector += feature_value
                    else:
                        feature_vector.append(feature_value)

            feature_matrix.append(feature_vector)

        return normalize(feature_matrix), feature_labels


    def get_training_and_test_sets(self, _percentage):
        """
        Divides the current features dataset into training and testing sets
        based on the given percentage.

        This function will use the current percentage value, which should be
        between 0 and 1 exclusively, to assess how many items should be stored
        in the training set. The remaining items will be stored in the testing
        sets. The function will return a tuple of FeatureData objects:

        (training_set, test_set) = feature_data.split(0.9)

        :param _percentage: The percentage of items to store in the training set.
        :return: A tuple containing the training set and test set.
        """
        assert _percentage > 0
        assert _percentage < 1

        ds1, ds2 = self.__split_by_percentage(_percentage)

        ds1_values, ds1_labels = ds1.__serialize_features_matrix()
        ds2_values, ds2_labels = ds2.__serialize_features_matrix()

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

        is1 = self._data[:_count]
        is2 = self._data[_count:]

        ds1 = FeatureData(is1)
        ds2 = FeatureData(is2)

        return ds1, ds2

    def serialize_features_matrix(self):
        features_values = []
        features_labels = []

        for featuredict in self._data.values():
            v, l = self.__serialize_features_dict(featuredict)
            features_values.append(v)
            features_labels.append(l)

        return features_values, features_labels

    def __serialize_features_matrix(self):
        """
        Converts the internal list of feature dictionaries into matrices
        containing the values of the features and labels in such a way
        they can be used with the scilearn-kit module.

        This function will use the FeatureData.__serialize_features_dict on
        each dictionary of features contained in the internal list of features.
        Each list of the resulting tuple (values, labels) will be stored in
        in their corresponding matrix in order to obtain 2 matrices; one
        containing all features values of the data set while the other will
        contain the corresponding labels. This function will return a tuple
        of matrices as:

        (features_values_matrix, features_labels_matrix) = \
            feature_data.__serialize_features_matrix()

        :return: A tuple of matrices (features_values_matrix, features_labels_matrix)
        """
        features_values = []
        features_labels = []

        for featuredict in self._data:
            v, l = self.__serialize_features_dict(featuredict)
            features_values.append(v)
            features_labels.append(l)

        return features_values, features_labels

    def __serialize_features_dict(self, _featuresdict):
        """
        Converts a dictionary of features into two lists; one list containing
        the values of the features and one list containing the corresponding
        label(s).

        This function will extract the values of each feature stored in the
        given dictionary and insert them in a list in the order they appear inthe
        dictionary. The labels will be stored in a separate list. Both lists are
        returned in a tuple in the format of (features_values, features_labels).

        :param _featuresdict: A dictionary containing Feature/values key pairs.
        :return: A tuple of 2 lists; one containing the values of the features, one
        containing a list of associated labels.
        """
        assert _featuresdict is not None
        features_values = []
        features_labels = []

        for f in _featuresdict.keys():
        #for f in _featuresdict.values():
            if f != Feature.LABEL:
                v = _featuresdict[f]
                if isinstance(v, list):
                    features_values += v
                else:
                    features_values.append(v)

        if Feature.LABEL in _featuresdict.keys():
            features_labels = _featuresdict[Feature.LABEL]

        return features_values, features_labels

    def save_features_to_json(self, _featureset, _destfile):
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
        for fdict in self._data.values():
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
            f.write(json.dumps(self._data))

    @staticmethod
    def load_features_from_json(_jsonfile):
        """
        Creates a FeatureData object filled with feature data extracted from
        a JSON file created using the FeatureSet.save_features_to_json().

        :param _jsonfile: A JSON file containing feature data.
        :return: A FeatureData object.
        """
        assert _jsonfile is not None
        assert os.path.isfile(_jsonfile)

        features_from_file = []

        with open(_jsonfile, "r") as f:
            json_data = json.load(f)

        # Replaces the keys with a Feature enum object
        for fdict in json_data.values():
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
                    elif skey == Feature.LOW_ASCII_FREQ.name:
                        # 32 to 127
                        v = [0] * 95
                        for bvalue in feature_value.keys():
                            v[int(bvalue)-32] = int(feature_value[bvalue])
                        fdict[Feature[skey]] = v
                        del fdict[skey]
                    elif skey == Feature.HIGH_ASCII_FREQ.name:
                        # 128 to 255
                        v = [0] * 128
                        for bvalue in feature_value.keys():
                            v[int(bvalue)-128] = int(feature_value[bvalue])
                        fdict[Feature[skey]] = v
                        del fdict[skey]
                    elif skey == Feature.LABEL.name:
                        # Single label for now:
                        fdict[Feature.LABEL] = feature_value[0]
                        del fdict[skey]
                    else:
                        fdict[Feature[skey]] = float(feature_value)
                        del fdict[skey]

            features_from_file.append(fdict)

        fd = FeatureData(features_from_file)
        return fd
