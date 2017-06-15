#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

import argparse
import sys
import timeit

from resyst import metadata
from resyst.dataset import *
from resyst import log
from resyst.features import *

def test():
    source_directory = "D:\\tmp\\govdocs\\debug"
    features_save_file = "D:\\tmp\\govdocs\\features.json"
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
