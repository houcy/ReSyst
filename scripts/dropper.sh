#!/bin/bash

N=20
SRC_FILE=""
DST_DIR=""
PREFIX=""

##### Functions
function usage
{
    echo "usage: $0 [[-s|--src] <file> [-c|--count] <count> [-d|--dest] <directory>]"
}

clear

while [ "$1" != "" ]; do
    case $1 in
        -s | --src  )           shift
                                SRC_FILE=$1
                                ;;
        -d | --dest )    		shift
								DST_DIR=$1
                                ;;
        -c | --count)    		shift
								N=$1
                                ;;								
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

if [ -z $DST_DIR ]; then
	echo "[-] Destination directory is missing."
	usage
	exit 1
fi

if [ ! -e $DST_DIR ]; then
	mkdir -p $DST_DIR
fi
	
if [ ! -e $SRC_FILE ]; then
	echo "[-] Could not find file: $SRC_FILE"
	exit 1
fi

if [ $N -lt 0 ]; then
	echo "[-] Invalid sample size: $N"
	exit 1
fi

echo "[=] Downloading $N file(s) from $SRC_FILE..."
for FILE in `shuf -n $N $SRC_FILE`; do
	echo "[>]	$FILE"
	wget --tries=45 --mirror -o dropper.log -e robots=off -A zip,pkg,rar,bin,img,gz,7z --ignore-case $FILE -P $DST_DIR &> /dev/null
done

echo "[+] Completed. Terminating..."
exit 0