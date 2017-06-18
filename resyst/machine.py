#!/usr/bin/env python
# coding: utf-8
"""
    package.module
    ~~~~~~~~~~~~~

    TODO: Module description

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
import random
from abc import *
from sklearn.neighbors import *
from sklearn.svm import *

class Classifier(metaclass=ABCMeta):

    def __init__(self):
        pass

    def __str__(self):
        return "<Classifier>"

    @abstractmethod
    def test_accuracy(self, _test_values, _test_labels, **kwargs):
        """
        Returns the accuracy of the classifier by attempting to predict the labels
        of the given test values.

        This function will iterate the test values given and predict its labels. If the
        result correspond to the labels provided, a success counter will be incremented.
        Once all tests have been evaluated, the ratio between successful predictions and
        the number of test samples will be returned.

        :param _test_values: A list of features to which one or more labels will be predicted.
        :param _test_labels:  The list of corresponding labels for each features vector provided.
        :param kwargs: Additional arguments.
        :return: A float value representing the accuracy of the classifier.
        """
        pass

    @abstractmethod
    def predict(self, _extracted_features, **kwargs):
        pass


class SVMClassifier(Classifier):

    def __init__(self, _C=256, _kernel='rbf', _gamma='auto'):
        super().__init__()
        self.svm = SVC(C=_C, kernel=_kernel, gamma=_gamma)

    def __str__(self):
        fmt = "<SVM C={cv:d}, kernel='{kv:s}', gamma={gv:s}>"
        return fmt.format(cv=self.svm.C, kv=self.svm.kernel, gv=str(self.svm.gamma))

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

    def __str__(self):
        fmt = "<KNN K={kv:d}>"
        return fmt.format(kv=self.knn.n_neighbors)


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

class RndClassifier(Classifier):

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "<RndClassifier>"

    def test_accuracy(self, _featureset, _training_to_test_ratio=0.9, **kwargs):
        [(training_values, training_labels), (test_values, test_labels)] = \
            _featureset.get_training_and_test_sets(_training_to_test_ratio)

        results = []
        choices = list(set(training_labels + test_labels))
        successful_predictions = 0

        for i in range(len(test_values)):
            response = random.choice(choices)
            expected = test_labels[i]
            if response == expected:
                successful_predictions += 1
            results.append((response, expected))

        accuracy = successful_predictions / float(len(test_values))
        return accuracy, results

    def predict(self, _extracted_features, **kwargs):
        response = random.choice(kwargs['choices'])
        return response
