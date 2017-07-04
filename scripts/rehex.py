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
import os
import sys
import argparse

from hexformat.srecord import SRecord
from hexformat.tektronix import TektronixExtHex
from hexformat.intelhex import IntelHex
#
# //////////////////////////////////////////////////////////////////////////////
# Constants and globals
#
FORMAT_SRECORD = 'srec'
FORMAT_IHEX = 'ihex'
FORMAT_TEKHEX = 'tek'
SUPPORTED_FORMATS = [FORMAT_SRECORD, FORMAT_IHEX, FORMAT_TEKHEX]
#
# //////////////////////////////////////////////////////////////////////////////
# Program Information
#
project = "Rehex"
version = '0.1'
description = 'Utility to convert binary files to Intel Hex, Motorola S-Record or Tektronic Hex'
authors = ['Jonathan Racicot']
authors_string = ', '.join(authors)
emails = ['cyberrecce@gmail.com']
license = 'MIT'
copyright = '2017 ' + authors_string
url = 'http://thecyberrecce.net'

author_strings = []
for name, email in zip(authors, emails):
    author_strings.append('Author: {0} <{1}>'.format(name, email))

epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
    project=project,
    version=version,
    authors='\n'.join(author_strings),
    url=url)
print(epilog)
#
# //////////////////////////////////////////////////////////////////////////////
#
# //////////////////////////////////////////////////////////////////////////////
# Argument Parser Declaration
#
arg_parser = argparse.ArgumentParser(
    prog=sys.argv[0],
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=description,
    epilog=epilog)
	
arg_parser.add_argument(
    '-V', '--version',
    action='version',
    version='{0} {1}'.format(project, version))

arg_parser.add_argument("-b", "--binary",
                        dest="binary_file",
						required=True,
                        help="Binary file to convert.")
arg_parser.add_argument("-f", "--format",
                        dest="output_format",
						required=True,
						choices=SUPPORTED_FORMATS,
                        help="Output format.")
arg_parser.add_argument("-o", "--output",
                        dest="hex_file",
						required=True,
                        help="Filename of the resulting hex file.")

#
# //////////////////////////////////////////////////////////////////////////////
#
# //////////////////////////////////////////////////////////////////////////////
# Main
#
def main(args):
	"""Program entry point.

	:param argv: command-line arguments
	:type argv: :class:`list`
	"""
	binary_file = args.binary_file
	output_format = args.output_format.lower()
	output_filename = args.hex_file
	
	if not os.path.isfile(binary_file):
		print("[-] Could not find binary file: '{f:s}'.".format(f=binary_file))
		sys.exit(1)
	
	try:	
		if output_format == FORMAT_SRECORD:
			srec = hexformat.SRecord.frombinfile(binary_file)
			srec.tosrecfile(output_filename)
		elif output_format == FORMAT_IHEX:
			ihex = hexformat.IntelHex.frombinfile(binary_file)
			ihex.toihexfile(output_filename)
		elif output_format == FORMAT_TEKHEX:
			tekhex = hexformat.tektronix.frombinfile(binary_file)
			tekhex.totekfile(output_filename)
	except Exception as e:
		print("[-] An error occured during conversion: {err:s}.".format(err=str(e)))
	else:
		print("[+] Created file '{of:s}' using {fmt:s} format.".format(of=output_filename, fmt=output_format))
	
if __name__ == '__main__':
    # entry_point()
    main(arg_parser.parse_args())						