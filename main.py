#!/usr/bin/env python
# -*- coding: utf-8 -*-
# //////////////////////////////////////////////////////////////////////////////
#
# Copyright (C) 2017 Jonathan Racicot
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http:#www.gnu.org/licenses/>.
#
# You are free to use and modify this code for your own software
# as long as you retain information about the original author
# in your code as shown below.
#
# <author>Jonathan Racicot</author>
# <email>cyberrecce@gmail.com</email>
# <date>2017-06-01</date>
# <url>https://github.com/infectedpacket</url>
# //////////////////////////////////////////////////////////////////////////////
#
# //////////////////////////////////////////////////////////////////////////////
# Imports Statements
#
from __future__ import print_function

import sys
import time
import argparse

from resyst import metadata
from resyst.machine import *
from resyst.dataset import *
from resyst.log import *
from resyst.features import *
from sklearn.preprocessing import normalize
from sklearn.datasets import dump_svmlight_file
import sklearn
from sklearn.neighbors import *
from sklearn.svm import *
from sklearn.model_selection import *
#
# //////////////////////////////////////////////////////////////////////////////
# Constants and globals
#
ACTION_TRAIN = 'train'
ACTION_TEST = 'test'
ACTION_PREDICT = 'predict'
ACTION_CLEAN = 'clean'

ACTIONS = [
    ACTION_TRAIN,
    ACTION_TEST,
    ACTION_PREDICT,
    ACTION_CLEAN,
    "debug"  # TODO: remove
]

#
# //////////////////////////////////////////////////////////////////////////////
# Program Information
#
author_strings = []
for name, email in zip(metadata.authors, metadata.emails):
    author_strings.append('Author: {0} <{1}>'.format(name, email))

epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
    project=metadata.project,
    version=metadata.version,
    authors='\n'.join(author_strings),
    url=metadata.url)
print(epilog)


#
# //////////////////////////////////////////////////////////////////////////////
#
# //////////////////////////////////////////////////////////////////////////////
# Argument Parser Declaration
#

def directory(value):
    if os.path.isdir(value):
        return value
    else:
        raise argparse.ArgumentTypeError("Invalid directory: {:s}".format(value))

available_features = {
        'bfd': Feature.BFD,
        'wfd': Feature.WFD,
        'shannonentropy': Feature.SHANNON_ENTROPY,
        'meanbytevalue': Feature.BYTE_VAL_MEAN,
        'stddevbytevalue': Feature.BYTE_VAL_STDDEV,
        'meanavgdevbytevalue': Feature.BYTE_VAL_MAD,
        'lowasciifreq': Feature.LOW_ASCII_FREQ,
        'highasciifreq': Feature.HIGH_ASCII_FREQ,
        'stdkurtosis': Feature.STD_KURTOSIS,
        'avgbytecont': Feature.AVG_BYTE_CONTINUITY,
        'longstreak': Feature.LONGEST_STREAK,
    }

def feature_list(_features_name):
    #features_name = value.lower().split(',')

    features = []
    for fname in _features_name:
        if fname in available_features.keys():
            features.append(available_features[fname])
        else:
            raise argparse.ArgumentTypeError("Unknown feature: {:s}".format(fname))
    return features


def ratio(value):
    try:
        v = float(value)
        if v <= 0 or v >= 1:
            raise argparse.ArgumentTypeError("Training to testing ratio must be between 0 and 1 exclusively.")
        return v
    except:
        raise argparse.ArgumentTypeError("Invalid ratio value: {:s}".format(str(value)))


arg_parser = argparse.ArgumentParser(
    prog=sys.argv[0],
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=metadata.description,
    epilog=epilog)
arg_parser.add_argument(
    '-V', '--version',
    action='version',
    version='{0} {1}'.format(metadata.project, metadata.version))
arg_parser.add_argument("-a", "--action",
                        dest="action",
                        choices=ACTIONS,
                        type=str.lower,
                        help="Specifies which action to perform.")
train_options = arg_parser.add_argument_group("Training Options", "Available options for training the program.")
train_options.add_argument("-sd", "--source-dir",
                           dest="source_directory",
                           type=directory,
                           help="Directory containing files to use for training purposes.")
train_options.add_argument("-of", "--output-file",
                           dest="training_results",
                           help="File into which the training results will be written for testing and prediction.")
train_options.add_argument("-f", "--features",
                           dest="selected_features",
                           choices=available_features.keys(),
                           type=str.lower,
                           nargs="+",
                           help="List of features to extract from the sample files.")
test_options = arg_parser.add_argument_group("Testing Options", "Available options for testing the program.")
test_options.add_argument("-tf", "--training-file",
                          dest="training_file",
                          help="File created as the result of the training file.")
test_options.add_argument("-tr", "--testing-ratio",
                          dest="testing_ratio",
                          type=ratio,
                          help="Training to testing ratio to use for accuracy estimation.")


#
# //////////////////////////////////////////////////////////////////////////////
#
# //////////////////////////////////////////////////////////////////////////////
# Main
#

def action_train_general_file_classification(_source_directory, _output_file, _features):
    """
    TODO: PyDoc
    :param _source_directory:
    :param _output_file:
    :param _features:
    :return:
    """
    assert _source_directory is not None
    assert os.path.isdir(_source_directory)
    assert _output_file is not None
    assert _features is not None
    assert len(_features) > 0

    info("Loading files from '{sd:s}'.".format(
        sd=_source_directory
    ))
    fileset = FileSet()
    start = time.perf_counter()
    fileset.load_from_directory(_source_directory)
    end = time.perf_counter()
    info("{fc:d} file(s) added to current data set in {ts:f} second(s).".format(
        fc=len(fileset), ts = (end-start)
    ))

    info("Labeling file objects...")
    files = fileset.data
    start = time.perf_counter()
    for fileobj in files.values():
        fileobj.set_extension_as_label()
    end = time.perf_counter()
    info("{fc:d} file(s) labelled in {ts:f} second(s).".format(
        fc=len(fileset), ts = (end-start)
    ))

    info("Extracting features from file set...")
    start = time.perf_counter()
    features = FeatureSet.extract_features_from_fileset(_features, fileset)
    end = time.perf_counter()
    info("{ftc:d} feature(s) extracted from {fc:d} file(s) in {ts:f} second(s).".format(
        ftc=len(fileset)*len(_features), fc=len(fileset), ts=(end-start)
    ))

    info("Saving extracted features...")
    start = time.perf_counter()
    features.save_features_to_json(features, _output_file)
    end = time.perf_counter()
    info("Saved {ftc:d} feature(s) to '{fs:s}' in {ts:f} second(s).".format(
        ftc=len(fileset)*len(_features), fs=_output_file, ts=(end-start)
    ))

def action_test_general_file_classification(_training_file, _training_to_test_ratio):
    assert _training_file is not None
    assert os.path.isfile(_training_file)
    assert _training_to_test_ratio > 0 and _training_to_test_ratio < 1

    info("Loading features from file...")
    start = time.perf_counter()
    features = FeatureData.load_features_from_json(_training_file)
    features_vectors, features_labels = features.to_feature_matrix()

    end = time.perf_counter()
    info("Loaded {ftc:d} feature(s) from '{fs:s}' in {ts:f} second(s).".format(
        ftc=len(features), fs=_training_file, ts=(end-start)
    ))

    info("Generating classifiers...")
    classifiers = []
    for k in [1, 3]:
        classifiers.append(KNeighborsClassifier(n_neighbors=k))

    info("Searching for optimal parameters for SVM classifier...")
    grid_search_space = [
        {
        'gamma': [2, 1, 0.01, 0.001],
        'C': [128, 256, 512, 1024, 2048, 4096, 8192],
        'kernel': ['rbf']
        },
        {
        'kernel' : ['linear'],
        'C': [128, 256, 512, 1024, 2048, 4096, 8192],
        }
    ]
    svc_grid_search = GridSearchCV(SVC(C=1), grid_search_space, cv=5,
                       scoring='precision_macro')
    svc_grid_search.fit(features_vectors, features_labels)
    info("Optimal parameters for SVM: ")
    for param in svc_grid_search.best_params_:
        info('\t{p:s}: {val:s}'.format(
            p=param,
            val=str(svc_grid_search.best_params_[param])))

    classifiers.append(SVC(C=svc_grid_search.best_params_['C'],
                           kernel=svc_grid_search.best_params_['kernel'],
                           gamma=svc_grid_search.best_params_['gamma']))
    classifiers.append(DecisionTreeClassifier())

    info("Conducting K-Fold Cross Validation...")
    start = time.perf_counter()
    max_accuracy = 0.0
    best_classifier = None
    for classifier in classifiers:
        info('-'*76)
        scores = cross_val_score(classifier,features_vectors, features_labels, cv=5)
        info("\tAccuracy: {acc:0.2f} (+/- {err:0.2f}):\n\t    Classifier: {cls:s}".format(
            cls=repr(classifier), acc=scores.mean(), err=(scores.std() * 2)))
        if scores.mean() > max_accuracy:
            max_accuracy = scores.mean()
            best_classifier = classifier

    end = time.perf_counter()
    info("Concluded validation of classifiers in {ts:f} second(s).".format(
        ts=(end-start)
    ))
    info("="*76)
    info("Maximum Accuracy: {ma:.4f}".format(ma=max_accuracy))
    info("Best Classifier : {bc:s}".format(bc=repr(best_classifier)))

def main(args):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """

    program_action = args.action

    if program_action == ACTION_TRAIN:
        source_directory = args.source_directory
        training_results_file = args.training_results
        features_to_extract = feature_list(args.selected_features)
        action_train_general_file_classification(
            _source_directory=source_directory,
            _features=features_to_extract,
            _output_file=training_results_file
        )
    elif program_action == ACTION_TEST:
        training_results_file = args.training_file
        training_to_test_ratio = args.testing_ratio
        action_test_general_file_classification(
            _training_file=training_results_file,
            _training_to_test_ratio=training_to_test_ratio
        )
    elif program_action == ACTION_PREDICT:
        error("Not implermented")

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    # entry_point()
    main(arg_parser.parse_args())