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
import json
import string
import argparse
import subprocess
import textract
from textblob import TextBlob

#
# //////////////////////////////////////////////////////////////////////////////
# Constants and globals
#
LABELS = [
	"MANUFACTURER",
	"DEVICE_MODEL",
	"DEVICE_TYPE",
	"FIRMWARE_VERSION",
	"OPERATING_SYSTEM",
	"DEVICE_COMPONENT"
]
#
# //////////////////////////////////////////////////////////////////////////////
# Program Information
#
project = "Retext"
version = '0.1'
description = 'Utility to label sentences from one or multiple documents.'
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

arg_parser.add_argument("-s", "--source",
                        dest="source_file",
						required=True,
                        help="File or directory containing documents to read sentences from.")
arg_parser.add_argument("-o", "--output",
                        dest="output_file",
						required=True,
                        help="File containing the results.")
#
# //////////////////////////////////////////////////////////////////////////////
# Functions
#
def get_fv(_sentence_no, _sentence, _np, _np_freq):
	assert _sentence is not None
	assert _np is not None
	assert len(_sentence.words) > 0
	assert len(_np) > 0
	
	KEYWORDS = ["copyright", "firmware", "version"]
	
	IDX_SENT_NO = 0
	IDX_SENT_WC = 1
	IDX_FIRST_CAPS_RATIO = 2
	IDX_CAPS_RATIO = 3
	IDX_SP_CHARS_CNT = 4
	IDX_DIGITS_LETTERS_RATIO = 5
	IDX_NP_CHAR_CNT = 6
	IDX_NP_FREQ = 7
	IDX_KEYWORDS = 8
	
	IDX_IS_CAPITALIZED = 3
	IDX_ALL_CAPS = 4

	s_words = list(map(lambda x: x.lower(), _sentence.words))
	nb_chars = len(_np)
	nb_digits = count_digits(_np)
	nb_special_chars = count_special_chars(_np)
	nb_words = len(_np.split(" "))
	nb_caps = get_caps_count(_np)
	nb_first_caps = get_first_chars_count(_np)
	np_freq_text = _np_freq[_np.lower()]
	
	fv = [0]*(IDX_NP_FREQ+len(KEYWORDS)+1)
	fv[IDX_SENT_NO] = _sentence_no
	fv[IDX_SENT_WC] = len(_sentence.words)
	fv[IDX_FIRST_CAPS_RATIO] = nb_first_caps/nb_words
	fv[IDX_CAPS_RATIO] = nb_caps/nb_chars
	fv[IDX_SP_CHARS_CNT] = nb_special_chars
	fv[IDX_DIGITS_LETTERS_RATIO] = nb_digits/float(nb_chars)
	fv[IDX_NP_CHAR_CNT] = nb_chars
	fv[IDX_NP_FREQ] = np_freq_text
	
	k_no = 0
	for k in KEYWORDS:
		if k in s_words: 
			fv[IDX_KEYWORDS+k_no] = 1
		else:
			fv[IDX_KEYWORDS+k_no] = 0
		k_no += 1
	
	return fv
	
def get_caps_count(_np):
	cc = 0
	for c in _np:
		if c.isupper(): cc += 1
	return cc/float(len(_np))
	
def get_first_chars_count(_np):
	c = 0
	ws = _np.split(" ")
	for w in ws:
		if w[0].isupper(): c+=1
	
	return float(c)
	
def count_special_chars(_np):
	special_chars = "@()\"\'-_,#:;"
	sc = 0
	for c in _np:
		if c in special_chars:
			sc += 1
	return sc
	
def count_digits(_np):
	sc = 0
	for c in _np:
		if c in string.digits:
			sc += 1
	return sc
	
# //////////////////////////////////////////////////////////////////////////////
# Main
#
def main(args):
	"""Program entry point.

	:param argv: command-line arguments
	:type argv: :class:`list`
	"""
	source_file = args.source_file
	output_file = args.output_file
	source_files= []
	
	if not os.path.isfile(source_file) and not os.path.isdir(source_file):
		print("[-] Source file/directory not found: '{sf:s}'.".format(sf=source_file))
		sys.exit(1)
		
	if os.path.isfile(source_file):
		source_files=[source_file]
	elif os.path.isdir(source_file):
		source_files = os.listdit(source_file)
	
	np_dict = {}
	stats = {
		"UNLABELLED": 0,
		"MANUFACTURER": 0,
		"DEVICE_MODEL": 0,
		"FIRMWARE_VERSION": 0,
		"OPERATING_SYSTEM": 0,
		"DEVICE_COMPONENT": 0
	}
	if os.path.isfile(output_file):
		print("[=] Loading results from '{db:s}'...".format(db=output_file))
		with open(output_file) as f:    
			np_dict = json.load(f)
		print("[=] Loaded {nb:d} noun phrase(s) from database.".format(nb=len(np_dict)))
		
		for k in np_dict.keys():
			labels = np_dict[k]["labels"]

			if len(labels) <=0 :
				stats["UNLABELLED"] += 1
			else:
				for l in labels:
					stats[l] += 1
					
		for s in stats.keys():
			print("\t{lbl:s}: {nb:d}".format(lbl=s, nb=stats[s])
	
	if len(source_files) > 0:
	
		wc = 0	# Word count
		terminate_program = False
		
		for file in source_files:
			# Extract text content from file.
			# Ref. https://textract.readthedocs.io/en/stable/
			text = str(textract.process(file, encoding='utf-8'))
			text = text.strip()
			
			# Windows/UNIX CR/LF issues and README txt
			# standardization
			text = text.replace('\\n', '.')
			text = text.replace('\\t', ' ')
			text = text.replace('\\r', '')
			text = text.replace('...', '.')
			
			# Enclosed extracted text in textblob
			# Ref. http://textblob.readthedocs.io/en/dev/quickstart.html
			tblob = TextBlob(text)
			
			print("[=] Processing '{sf:s}'. {nbs:d} sentence(s).".format(
				sf=file, nbs=len(tblob.sentences)))
				
			sentence_no = 0
			for s in tblob.sentences:
				# Exit loop if user typed 'quit'
				if terminate_program: 
					with open(output_file, "w") as f:
						np_json = json.dumps(np_dict, indent=4, separators=(',', ': '))
						f.write(np_json)
					print("[+] Saved labelled noun phrases.")
					break
				
				# Otherwise extract noun phrases from sentence
				nnp = s.noun_phrases
				
				# Label each noun phrase
				for np in nnp:
					
					# Increase word count
					wc += 1
					
					# Find capitalized version
					np_idx = s.lower().find(np)
					if np_idx > -1:
						cnp = s[np_idx:np_idx+len(np)]
					else:
						cnp = np
					
					# Standardize the noun phrase
					np = ''.join(filter(lambda x: x in string.printable, np))
					cnp = ''.join(filter(lambda x: x in string.printable, cnp)) 
					
					# If not already processed earlier, ask for labels
					if not cnp in np_dict.keys() and len(np) > 0:
						# Clear the screen to avoid mislabelling
						subprocess.call('clear', shell=True)
						
						# Extract the feature vector
						fv = get_fv(sentence_no, s, cnp, tblob.np_counts)
						
						print("Sentence: ")
						print(s)
						print("")
						print("Noun phrase: '{cnp:s}' ({np:s})".format(cnp=cnp, np=np))
						print("")
						print("Features vector:")
						print(fv)
						print("")
						
						# Display available labels
						for i in range(0, len(LABELS)):
							print("[{ix:d}] {lbl:s}".format(ix=i, lbl=LABELS[i]))
						labels_no = input("[<] [{ch:s}]: ".format(ch=','.join(list(map(str, range(0, len(LABELS))))+["none", "quit"])))

						# No labels for this NP
						if labels_no == "none" or len(labels_no) <= 0:
							np_dict[cnp] = {
									"labels" : [],
									"fv"	: fv
								}
						# Terminate labelling
						elif labels_no == "quit":
							terminate_program = True
							break
						else:
							l = []
							w_labels = []
							try:
								l = list(map(lambda x: int(x, 10), labels_no.split(",")))
							except:
								lbls = labels_no.split(",")
								for i in lbls:
									if i.isdigit(): l.append(i)
									
							# Check to make sure input is valid
							for ix in l:
								if ix >= 0 and ix < len(LABELS):
									w_labels.append(LABELS[ix])
									
							if len(w_labels) > 0:
								np_dict[cnp] = {
										"labels:" : w_labels,
										"fv" : fv
									}
							else:
								np_dict[cnp] = {
										"labels:" : [],
										"fv" : fv
									}
				
					# Save progress every 10 words labelled.
					if wc % 10 == 0:
						with open(output_file, "w") as f:
							np_json = json.dumps(np_dict, indent=4, separators=(',', ': '))
							f.write(np_json)
						print("[+] Saved labelled noun phrases.")
						
				sentence_no += 1
			
if __name__ == '__main__':
    # entry_point()
    main(arg_parser.parse_args())	