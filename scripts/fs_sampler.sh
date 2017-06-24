#!/bin/bash

N=200
S=25
MIN_F=10
MAX_F=100
SKIP_SAMPLING=1
SKIP_TRAINING=0
SRC=../data/training/govdocs
DST=../data/training/filesystem
TEST=../data/testing/fs
FS=(sqsh bfs ext3 fat msdos vfat cramfs ext4 jffs2 ntfs ext2)

clear

if [ ! -e $RESYST ]; then
	echo [-] Could not find ReSyst launcher: $RESYST
	exit 1
fi

if [ ! -e $SRC ]; then
	echo [-] Could not find source directory: $SRC
	exit 1
fi

if [ ! -e $DST ]; then
	mkdir -p $DST
fi

echo "[=] Generating $N file systems..."
for i in `seq 1 $N`; do
	FILESYS=${FS[$RANDOM % ${#FS[@]}]}
	NB_F=$(($MIN_F + $RANDOM % $MAX_F))
	FNAME=`cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32`
	FS_FILE=$DST/$FNAME.$FILESYS
	TMP_DIR=`mktemp -d -t resyst`
	find $SRC -type f | sort -R | tail -$NB_F | while read FILE; do
		cp $FILE $TMP_DIR
	done
	
	if [ -e mkfs.$FILESYS ]; then
		
	fi

	echo "[>]\t$FS_FILE ($NB_F)"
	
	rm -rf $TMP_DIR
done

echo "[+] Completed. Terminating."
exit 0