#!/usr/bin/env python
# coding: utf-8
"""
    package.module
    ~~~~~~~~~~~~~

    TODO: Module description

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
from abc import *
from sklearn.neighbors import *
from sklearn.svm import *

class Classifier(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def test_accuracy(self, _test_values, _test_labels, **kwargs):
        pass

    @abstractmethod
    def predict(self, _extracted_features, **kwargs):
        pass


class SVMClassifier(Classifier):

    def __init__(self, _C=256, _kernel='rbf', _gamma='auto'):
        super().__init__()
        self.svm = SVC(C=_C, kernel=_kernel, gamma=_gamma)

    def test_accuracy(self, _featureset, _training_to_test_ratio = 0.9, **kwargs):
        [(training_values, training_labels), (test_values, test_labels)] = \
            _featureset.get_training_and_test_sets(_training_to_test_ratio)
        results = []
        self.svm.fit(training_values, training_labels)
        successful_predictions = 0
        for i in range(len(test_values)):
            response = self.svm.predict(test_values[i])
            expected = test_labels[i]
            if response == expected:
                successful_predictions += 1
            results.append((response, expected))

        accuracy = successful_predictions / float(len(test_values))
        return accuracy, results

    def predict(self, _extracted_features, **kwargs):
        response = self.svm.predict(_extracted_features)
        return response

class KNNClassifier(Classifier):

    def __init__(self, _k = 3):
        super().__init__()
        self.knn = KNeighborsClassifier(n_neighbors=_k)

    def test_accuracy(self, _featureset, _training_to_test_ratio = 0.9, **kwargs):
        [(training_values, training_labels), (test_values, test_labels)] = \
            _featureset.get_training_and_test_sets(_training_to_test_ratio)

        results = []
        self.knn.fit(training_values, training_labels)
        successful_predictions = 0
        for i in range(len(test_values)):
            response = self.knn.predict(test_values[i])
            expected = test_labels[i]
            if response == expected:
                successful_predictions += 1
            results.append((response, expected))

        accuracy = successful_predictions / float(len(test_values))
        return accuracy, results

    def predict(self, _extracted_features, **kwargs):
        response = self.knn.predict(_extracted_features)
        return response
