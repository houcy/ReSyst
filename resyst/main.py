#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

import argparse
import sys
import timeit
from sklearn.neighbors import *
from sklearn.svm import *

from resyst import metadata
from resyst.dataset import *
from resyst import log
from resyst.features import *

def test():
    skip_training = True
    source_directory = "D:\\tmp\\govdocs\\001"
    features_save_file = "D:\\tmp\\govdocs\\features.json"
    features_load_file = features_save_file
    if not skip_training:
        fileset = DataSet()
        log.info("Loading file set from '{sd:s}'.".format(
            sd = source_directory
        ))
        fileset.load_from_directory(source_directory)
        log.info("{fc:d} file(s) loaded from '{sd:s}'.".format(
            fc = len(fileset),
            sd = source_directory
        ))

        files = fileset.data
        for fileobj in files.values():
            fileobj.set_extension_as_label()

        features_to_extract = [
            Feature.BFD
        ]

        log.info("Extracting {fc:d} feature(s):".format(
            fc = len(features_to_extract)
        ))
        for f in features_to_extract:
            log.info("\t{fn:s}".format(fn=f))

        features_extracted = FeatureSet.extract_features_from_dataset(
            features_to_extract, fileset
        )

        log.info("Total of {fc:d} feature(s) extracted from {fss:d} file(s).".format(
            fc = len(features_to_extract) * len(fileset),
            fss = len(fileset)
        ))

        log.info("Saving features to '{ff:s}'...".format(
            ff = features_save_file
        ))
        FeatureSet.save_features_to_json(features_extracted, features_save_file)
        log.info("Completed")

    features_load_file = features_save_file
    log.info("Retrieving features from '{fs:s}'...".format(
        fs = features_load_file
    ))
    features_from_file = FeatureSet.load_features_from_json(features_load_file)
    log.info("Extracted features from {sc:d} sample(s).".format(
        sc = len(features_from_file)
    ))

    #Experimental from here:

    features_matrix = FeatureSet.serialize_features_matrix(features_from_file)
    (training_set, test_set) = FeatureSet.split_matrix(features_matrix, int(len(features_matrix)*0.9))
    training_values, training_labels = FeatureSet.split_values_and_labels(training_set)
    #test_values, test_labels = FeatureSet.split_values_and_labels(test_set)


    info("Applying KNN (k=3) on testing set...")
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(training_values, training_labels)
    successful_prediction = 0
    for (test_sample, test_label) in test_set:
        response = knn.predict((test_sample, ))
        if response == test_label:
            info("\tExpected: {ea:s}\tPrediction: {pa:s}".format(
                ea = test_label, pa = response[0]
            ))
            successful_prediction += 1
        else:
            error("\tExpected: {ea:s}\tPrediction: {pa:s}".format(
                ea = test_label, pa = response[0]
            ))

    accuracy = successful_prediction/float(len(test_set))
    info("Estimated accuracy: {a:.4f}".format(a=accuracy))

    info("Applying SVM (C=256) on testing set...")
    svm = SVC(C=1024, kernel='linear')
    svm.fit(training_values, training_labels)
    successful_prediction = 0
    for (test_sample, test_label) in test_set:
        response = svm.predict((test_sample, ))
        if response == test_label:
            info("\tExpected: {ea:s}\tPrediction: {pa:s}".format(
                ea = test_label, pa = response[0]
            ))
            successful_prediction += 1
        else:
            error("\tExpected: {ea:s}\tPrediction: {pa:s}".format(
                ea = test_label, pa = response[0]
            ))

    accuracy = successful_prediction/float(len(test_set))
    info("Estimated accuracy: {a:.4f}".format(a=accuracy))

def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
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

    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=epilog)
    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version))

    arg_parser.parse_args(args=argv[1:])

    print(epilog)

    test()
    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    #entry_point()
    main(sys.argv)
