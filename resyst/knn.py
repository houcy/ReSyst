#!/usr/bin/env python
# coding: utf-8
"""
    resyst.knn
    ~~~~~~~~~~~~~

    TODO: Description

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
import math
from resyst.dataset import DataSet

class knn(object):
    @staticmethod
    def find_neighbors(self, _trainset, _test, _k):
        import operator
        distances = []
        length = len(_test)-1
        for training_item in _trainset:
            d = self.euclidian_distance(training_item, _test)
            distances.append((training_item, d))
        distances.sort(key=operator.itemgetter(1))
        neighbors = []
        for i in range(_k):
            neighbors.append(distances[i][0])
        return neighbors

    @staticmethod
    def euclidian_distance(_features1, _features2):
        assert len(_features1) == len(_features2)
        distance = 0
        count = len(_features1)-1
        for i in range(count):
            distance += pow((_features1[i] - _features2[i]), 2)
        return math.sqrt(distance)
