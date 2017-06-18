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


def feature_list(value):
    features_name = value.lower().split(',')
    available_features = {
        'bfd': Feature.BFD,
        'wfd': Feature.WFD,
        'ShannonEntropy': Feature.SHANNON_ENTROPY,
        'MeanByteValue': Feature.BYTE_VAL_MEAN,
        'StdDevByteValue': Feature.BYTE_VAL_STDDEV,
        'MeanAvgDevByteValue': Feature.BYTE_VAL_MAD,
        'LowAsciiFreq': Feature.LOW_ASCII_FREQ,
        'HighAsciiFreq': Feature.HIGH_ASCII_FREQ,
        'StdKurtosis': Feature.STD_KURTOSIS,
        'AvgByteCont': Feature.AVG_BYTE_CONTINUITY,
        'LongStreak': Feature.LONGEST_STREAK,

    }

    features = []
    for fname in features_name:
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
                           type=feature_list,
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
def test2():
    source_directory = "D:\\tmp\\govdocs\\debug"
    features_save_file = "D:\\tmp\\govdocs\\features_tst.json"
    features = [ Feature.BFD, Feature.SHANNON_ENTROPY]
    action_train_general_file_classification(
        source_directory, features_save_file, features
    )

def test():
    skip_training = False
    source_directory = "D:\\tmp\\govdocs\\debug"
    features_save_file = "D:\\tmp\\govdocs\\features_zip.json"
    features_load_file = features_save_file
    training_to_test_ratio = 0.9

    if not skip_training:
        # fileset = DataSet()

        info("Loading file set from '{sd:s}'.".format(
            sd=source_directory
        ))
        start = time.perf_counter()
        fileset = CompressedFileDataSet.generate_from_directory(source_directory)
        end = time.perf_counter()
        info("Compressed file data set generation completed in {d:.4f} second(s).".format(
            d=(end - start)
        ))

        # fileset.load_from_directory(source_directory)
        info("{fc:d} file(s) loaded from '{sd:s}'.".format(
            fc=len(fileset),
            sd=source_directory
        ))

        files = fileset.data
        for fileobj in files.values():
            fileobj.set_extension_as_label()

        features_to_extract = [
            Feature.SHANNON_ENTROPY,
            Feature.BFD
        ]

        info("Extracting {fc:d} feature(s):".format(
            fc=len(features_to_extract)
        ))
        for f in features_to_extract:
            info("\t{fn:s}".format(fn=f))

        features_extracted = FeatureSet.extract_features_from_dataset(
            features_to_extract, fileset
        )

        info("Total of {fc:d} feature(s) extracted from {fss:d} file(s).".format(
            fc=len(features_to_extract) * len(fileset),
            fss=len(fileset)
        ))

        info("Saving features to '{ff:s}'...".format(
            ff=features_save_file
        ))
        FeatureSet.save_features_to_json(features_extracted, features_save_file)
        info("Completed")

    features_load_file = features_save_file
    info("Retrieving features from '{fs:s}'...".format(
        fs=features_load_file
    ))

    features_from_file = FeatureData.load_features_from_json(features_load_file)
    info("Extracted features from {sc:d} sample(s).".format(
        sc=len(features_from_file)
    ))

    k = 3
    C = 256
    kernel = 'linear'
    gamma = 2
    knn = KNNClassifier(_k=k)
    svm = SVMClassifier(_C=C, _kernel=kernel, _gamma=gamma)

    knn_accuracy, _ = knn.test_accuracy(features_from_file, _training_to_test_ratio=training_to_test_ratio)
    svm_accuracy, _ = svm.test_accuracy(features_from_file, _training_to_test_ratio=training_to_test_ratio)

    info("KNN-{kv:d}: Estimated accuracy: {av:.4f}".format(kv=k, av=knn_accuracy))
    info("SVM (C={cv:d}, kernel='{kv:s}', gamma='{gv:.2f}'): Estimated accuracy: {av:.4f}".format(
        cv=C, kv=kernel, gv=gamma, av=svm_accuracy))

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
    end = time.perf_counter()
    info("Loaded {ftc:d} feature(s) from '{fs:s}' in {ts:f} second(s).".format(
        ftc=len(features), fs=_training_file, ts=(end-start)
    ))

    info("Generating classifiers...")
    classifiers = []
    for k in [1, 3]:
        classifiers.append(KNNClassifier(_k=k))

    for C in [2, 64, 128, 256]:
        for kernel in ['linear', 'rbf']:
            for gamma in [1, 2]:
                classifiers.append(SVMClassifier(_C=C, _kernel=kernel, _gamma=gamma))

    classifiers.append(RndClassifier())

    report = {}
    avg_accuracy = 0.0
    max_accuracy = 0.0
    best_classifier = None
    info("Calculating accuracy for classifiers...")
    for classifier in classifiers:
        info("\t{cn:s}".format(cn=str(classifier)))
        accuracy, _ = classifier.test_accuracy(features, _training_to_test_ratio)
        avg_accuracy += accuracy
        report[str(classifier)] = accuracy
        if accuracy > max_accuracy:
            max_accuracy = accuracy
            best_classifier = str(classifier)

    avg_accuracy = avg_accuracy / len(classifiers)

    info("Accuracy Report")
    info("=" * 76)

    for classifier_name in report.keys():
        classifier_accuracy = report[classifier_name]
        info("\t{a:.4f}:\t{cn:s}".format(
            a = classifier_accuracy, cn=classifier_name
        ))
    info("=" * 76)
    info("Average Accuracy: {aa:.4f}".format(aa=avg_accuracy))
    info("Maximum Accuracy: {ma:.4f}".format(ma=max_accuracy))
    info("Best Classifier : {bc:s}".format(bc=best_classifier))

def main(args):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """

    program_action = args.action

    if program_action == ACTION_TRAIN:
        source_directory = args.source_directory
        training_results_file = args.training_results
        features_to_extract = args.selected_features
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
    else:
        test2()
    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    # entry_point()
    main(arg_parser.parse_args())
