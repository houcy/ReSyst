#!/bin/bash

N_PT=20
N_AB=20
N_BT=20
N_FB=20
HEX_SCRIPT=./rehex.py
HEX_FORMATS=(ihex srec tek)
SRC=../data/training/
SRC_BT=$SRC/govdocs
SRC_AB=$SRC/content_type/binary
SRC_PT=$SRC/govdocs
DST=../data/training/datatype
DST_PT=$DST/plain-text
DST_AB=$DST/ascii-binary
DST_BT=$DST/binary-text
DST_FB=$DST/full-binary
TEST=../data/testing/dt_sample
RESYST=../main.py
CREATE_SAMPLES=1
TRAIN_RESYST=0
TRG_RESULTS=../data/results/bt_trg_results.json
ACC_RESULTS=../data/results/bt_acc_results.txt
FEATURES="bfd"
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

if [ ! -e $HEX_SCRIPT ]; then
	echo [-] Could not find Rehex program: $HEX_SCRIPT
	exit 1
fi

if [ ! -e $SRC ]; then
	echo [-] Could not find source directory: $SRC
	exit 1
fi

if [ ! -e $DST ]; then
	mkdir -p $DST
	mkdir -p $DST_PT
	mkdir -p $DST_AB
	mkdir -p $DST_BT
	mkdir -p $DST_FB
fi

if [ $CREATE_SAMPLES -eq 1 ]; then
	echo "[!] Copying $N_PT plain text file(s) from $SRC_PT to $DST_PT..."
	find $SRC_PT -regextype posix-egrep -regex ".*\.(txt|rtf|html|1st)$" -type f | sort -R | tail -$N_PT | while read FILE; do
		cp -f "$FILE" "$DST_PT"
	done

	echo "[!] Copying $N_BT binary text file(s) from $SRC_BT to $DST_BT..."
	find $SRC_PT -regextype posix-egrep -regex ".*\.(doc|pdf|xls|docx)$" -type f | sort -R | tail -$N_BT | while read FILE; do
		cp -f "$FILE" "$DST_BT"
	done
	
	echo "[!] Generating $N_AB ASCII-formatted binary files from $SRC_AB to $DST_AB..."
	find $SRC_AB -type f | sort -R | tail -$N_BT | while read FILE; do
		HEX_TYPE=${HEX_FORMATS[$RANDOM % ${#HEX_FORMATS[@]}]}
	done
fi
	
if [ $TRAIN_RESYST -eq 1 ]; then
	if [ -e $RESYST ]; then
		python3 $RESYST -a train -sd $TEST -of $TRG_RESULTS -f $FEATURES
		python3 $RESYST -a test -tf $TRG_RESULTS -tr 0.9  > $ACC_RESULTS
		python3 $RESYST -a test -tf $TRG_RESULTS -tr 0.67 >> $ACC_RESULTS
	else
		echo [-] Could not find ReSyst launcher: $RESYST
	fi
fi