#!/bin/bash

FS=""
SRC=""
DST=""
SUPPORTED=(uboot sqsh bfs ext3 fat msdos iso vfat cramfs ext4 jffs2 ntfs ext2)
COMP=(gzip lzma lzo lz4 xz)
UBOOT=()

##### Functions
function usage
{
    echo "usage: $0 [[-s|--src] <directory>] [[-d|--dest] <file>] [-c <count>] [-f|--fs $SUPPORTED]"
}

function install_pkg
{
	PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $1 |grep "install ok installed")
	if [ "" == "$PKG_OK" ]; then
	  echo "[=] Installing package '$1'..."
	  sudo apt-get --force-yes --yes install $1 &> /dev/null
	fi
}

install_pkg squashfs-tools
install_pkg genisoimage

while [ "$1" != "" ]; do
    case $1 in
        -s | --src  )           shift
                                SRC=$1
                                ;;
        -d | --dest )    		shift
								DST=$1
                                ;;
        -f | --filesys)    		shift
								FS=$1
                                ;;								
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

if [ -z $SRC ]; then
	echo "[-] Failed to find source directory: $SRC."
	exit 1
fi

if [ -z $FS ]; then
	echo "[-] No output file system format specified."
	exit 1
fi

if [ -z $DST ]; then
	echo "[-] No output file specified."
	exit 1
fi

if [ $FS = "cramfs" ]; then
	mkfs.cramfs $SRC $DST.cramfs &> /dev/null
elif [ $FS = "uboot" ]; then
	IMAGE_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)
	mkimage -A arm - O linux -T kernel -C none -a 0x8000 -e 0x8000 -n $IMAGE_NAME -f $SRC $DST.uboot &> /dev/null
elif [ $FS = "sqsh" ]; then
	COMP_TYPE=${COMP[$RANDOM % ${#COMP[@]}]}
	mksquashfs $SRC/* $DST.sqsh -comp $COMP_TYPE &> /dev/null
elif [ $FS = "jffs2" ]; then
	mkfs.jffs2 --root $SRC -o $DST.jffs2 &> /dev/null
elif [ $FS = "iso" ]; then
	genisoimage -o $DST.iso $SRC &> /dev/null
else
	echo "[-] Unknown filesystem format: $FS."
	exit 1
fi

exit 0