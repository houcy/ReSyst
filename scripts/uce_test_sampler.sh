#!/bin/bash

N=200
C_U=150
C_C=200
C_E=120
SKIP_SAMPLING=1
SKIP_TRAINING=1
SRC=../data/training/govdocs
DST=../data/training/datatype
TEST=../data/testing/uce_sample
RESYST=../main.py
TRG_RESULTS=../data/results/uce_trg_results.json
ACC_RESULTS=../data/results/uce_acc_results.txt
CLF_FILE=../data/results/classifier.pkl
FEATURES="bfd StdKurtosis ShannonEntropy"
: << 'END'
usage: D:/src/resyst/ReSyst/resyst/main.py [-h] [-V]
                                           [-a {train,test,predict,clean,debug}]
                                           [-sd SOURCE_DIRECTORY]
                                           [-of TRAINING_RESULTS]
                                           [-f SELECTED_FEATURES]
                                           [-tf TRAINING_FILE]
                                           [-tr TESTING_RATIO]

Automatic reverse engineering of firmware files for embedded devices.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -a {train,test,predict,clean,debug}, --action {train,test,predict,clean,debug}
                        Specifies which action to perform.

Training Options:
  Available options for training the program.

  -sd SOURCE_DIRECTORY, --source-dir SOURCE_DIRECTORY
                        Directory containing files to use for training
                        purposes.
  -of TRAINING_RESULTS, --output-file TRAINING_RESULTS
                        File into which the training results will be written
                        for testing and prediction.
  -f {MeanAvgDevByteValue,AvgByteCont,LongStreak,MeanByteValue,
      ShannonEntropy,LowAsciiFreq,HighAsciiFreq,StdDevByteValue,
	  wfd,StdKurtosis,bfd}
                        List of features to extract from the sample files.

Testing Options:
  Available options for testing the program.

  -tf TRAINING_FILE, --training-file TRAINING_FILE
                        File created as the result of the training file.
  -tr TESTING_RATIO, --testing-ratio TESTING_RATIO
                        Training to testing ratio to use for accuracy
                        estimation.
END

clear

if [ ! -e $RESYST ]; then
	echo [-] Could not find ReSyst launcher: $RESYST
	exit 1
fi

if [ ! -e $SRC ]; then
	echo [-] Could not find source directory: $SRC
	exit 1
fi

if [ $SKIP_SAMPLING -eq 0 ]; then
	echo "[!] Erasing previously generated files..."
	rm -rf $DST/plain/ &> /dev/null
	rm -rf $DST/compressed/ &> /dev/null
	rm -rf $DST/encrypted/ &> /dev/null
	rm -rf $TEST &> /dev/null
	mkdir -p $TEST &> /dev/null

	echo "[=] Copying $N uncompressed file(s) from $SRC to $DST"
	./sampler.sh -s $SRC -d $DST/plain -c $N

	for FILE in $DST/plain/*; do
		mv "$FILE" "$FILE.uncompressed"
	done

	echo "[=] Generating $N compressed file(s) from $SRC to $DST"
	./sampler.sh -s $SRC -d $DST/compressed -c $N -z

	for FILE in $DST/compressed/*; do
		mv "$FILE" "$FILE.compressed"
	done

	echo "[=] Generating $N encrypted file(s) from $SRC to $DST"
	./sampler.sh -s $SRC -d $DST/encrypted -c $N -e

	for FILE in $DST/encrypted/*; do
		mv "$FILE" "$FILE.encrypted"
	done

	echo "[=] Creating testing sample"
	echo "[>]	Selecting $C_U uncompressed files from $DST/plain/"
	echo "[>]	Selecting $C_C uncompressed files from $DST/compressed/"
	echo "[>]	Selecting $C_E uncompressed files from $DST/encrypted/"

	./sampler.sh -s $DST/plain/ -d $TEST -c $C_U
	./sampler.sh -s $DST/compressed/ -d $TEST -c $C_C
	./sampler.sh -s $DST/encrypted/ -d $TEST -c $C_E

	echo "[+] Sample creation completed."
fi
	
if [ -e $RESYST ]; then
	if [ $SKIP_TRAINING -ne 1 ]; then
		python3 $RESYST -a train -sd $TEST -of $TRG_RESULTS -f $FEATURES
	fi
	python3 $RESYST -a test -tf $TRG_RESULTS -tr 0.9 -cf $CLF_FILE > $ACC_RESULTS
	python3 $RESYST -a test -tf $TRG_RESULTS -tr 0.67 -cf $CLF_FILE >> $ACC_RESULTS
else
	echo [-] Could not find ReSyst launcher: $RESYST
fi