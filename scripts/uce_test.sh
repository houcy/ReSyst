#!/bin/bash
TEST=../data/testing/uce_sample
RESYST=../main.py
TRG_RESULTS=../data/results/uce_trg_results.json
ACC_RESULTS=../data/results/uce_acc_results.txt
FEATURES="StdKurtosis LowAsciiFreq ShannonEntropy"

if [ -e $RESYST ]; then
	python3 $RESYST -a train -sd $TEST -of $TRG_RESULTS -f $FEATURES
	if [ -e $TRG_RESULTS ]; then
		python3 $RESYST -a test -tf $TRG_RESULTS -tr 0.9  > $ACC_RESULTS
		python3 $RESYST -a test -tf $TRG_RESULTS -tr 0.67 >> $ACC_RESULTS
	else
		echo "[-] Failed to create training file."
	fi
else
	echo [-] Could not find ReSyst launcher: $RESYST
fi