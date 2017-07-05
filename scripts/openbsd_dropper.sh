#!/bin/bash

N=30
DST_DIR=../data/training/datatype/full-binary
SRC_DIR=../data/training/urls
FILE_PREFIX="openbsd-6.1-pkgs-"
ARCH=(alpha amd64 arm hppa i386 mips64 powerpc sparc64)
CLEAN=1
UNTAR=0
DOWNLOAD=0
DELETE_TAR=0

if [ $DOWNLOAD -eq 1 ]; then
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
			tar -zxf $DROP_DIR/$URL_FILE bin
			if [ $DELETE_TAR -eq 1 ]; then
				rm -rf $DROP_DIR/$URL_FILE
			fi
		done
	done
	echo "[+] Download completed."
fi

if [ $UNTAR -eq 1 ]; then
	for A in "${ARCH[@]}"; do
		ARCH_DIR=$DST_DIR/$A
		find $ARCH_DIR -type f -name "*.tgz" | while read FILE; do
			echo "[=] Unarchiving $FILE..."
			tar -C $ARCH_DIR -zxf $FILE bin 2> /dev/null
		done
	done
	echo "[+] Unarchiving completed."
fi

if [ $CLEAN -eq 1 ]; then
	find $DST_DIR -regextype posix-egrep -regex ".*\.(sh|config|cfg|pl|py)$" -type f | while read FILE; do
		rm -rf $FILE
	done
	
	if [ $DELETE_TAR -eq 1 ]; then
		find $DST_DIR -regextype posix-egrep -regex ".*\.(sh|config|cfg|pl|py)$" -type f | while read FILE; do
			rm -rf $FILE
		done
	fi
	echo "[+] Cleaning completed."
fi

