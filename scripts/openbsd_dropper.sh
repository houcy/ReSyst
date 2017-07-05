#!/bin/bash

N=30
DST_DIR=../data/training/datatype/full-binary
SRC_DIR=../data/training/urls
FILE_PREFIX="openbsd-6.1-pkgs-"
ARCH=(alpha amd64 arm hppa i386 mips64 powerpc sparc64)
CLEAR=

for A in "${ARCH[@]}"; do
	DROP_DIR=$DST_DIR/$A
	if [ ! -e $DROP_DIR ]; then
		mkdir -p $DROP_DIR
		echo "[+] Created destination directory '$DROP_DIR'."
	fi

	FILE="$SRC_DIR/$FILE_PREFIX$A.txt"
	echo "[=] Downloading $N $A binary file(s) listed in $FILE"
	cat $FILE | sort -R | tail -$N | while read URL; do
		URL=${URL//[$'\t\r\n']}
		URL_FILE=${URL##*/}
		echo "[>]	$URL_FILE"
		wget -nH -nd --tries=5 --mirror -o dropper.log $URL -P $DROP_DIR &> /dev/null
		tar -zxvf $DROP_DIR/$URL_FILE bin
	done
done

echo "[+] Download completed."