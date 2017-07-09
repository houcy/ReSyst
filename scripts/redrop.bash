#!/bin/bash
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

# ReSyst 1.0
# Method
# -----------------------------------------------------
# 1) Create the directory tree for collections and samples
# 2) Download repositories
# 	2.1) Download GovDocs packages
#	2.2) Download OpenBSD packages
#	2.3) Download Firmware files
# 3) Create collections
# 	3.1) Create plain-text file collection
#	3.2) Create binary documents file collection
#	3.3) Create full-binary file collection
#	3.4) Generate ascii-formatted binary file collection
#	3.5) Generate file systems collection 
# 4) Generate samples
#	4.1) Generate uncompressed file samples
#	4.2) Generate compressed file samples
#	4.3)	Generate encrypted file samples
# 5) Generate classifiers
#	5.1) Generate U/C/E classifier 
#	5.2) Generate P/A/B/F classifier
#	5.3) Generate keyword classifier
# 6) Test classifiers
#	6.1)	Generate report for U/C/E classifier
#	6.2)	Generate report for P/A/B/F classifier
#	6.3) Generate report for keyword classifier

# //////////////////////////////////////////////////////////////////////////////
# Variables and parameters
# //////////////////////////////////////////////////////////////////////////////
#
# Log file
# --------
LOG_FILE="recollect.log"
#
# URL Archives
URL_ARCHIVE="urls.zip"
#
# Arrays
# ------
ARCH=(alpha amd64 arm hppa i386 mips64 powerpc sparc64)
ARCHIVES=(.zip .tar.gz .bz2 .lzip .lzop .lzma .rar .lha .ace .arj .cpio .arc .7z)
FSYS=(sqsh cramfs jffs2)
HEX_FORMATS=(ihex srec tek)
CRYPTOS=(bf-cbc bf bf-cfb bf-ecb bf-ofb cast-cbc cast cast5-cbc cast5-cfb cast5-ecb cast5-ofb des-cbc des des-cfb des-ofb des-ecb des-ede-cbc des-ede des-ede-cfb des-ede-ofb des-ede3-cbc des-ede3 des3 des-ede3-cfb des-ede3-ofb desx rc2-cbc rc2 rc2-cfb rc2-ecb rc2-ofb rc2-64-cbc rc2-40-cbc rc4 rc4-40 aes-128-cbc aes-192-cbc aes-256-cbc aes-128-cfb aes-192-cfb aes-256-cfb aes-128-cfb1 aes-192-cfb1 aes-256-cfb1 aes-128-cfb8 aes-192-cfb8 aes-256-cfb8 aes-128-ecb aes-192-ecb aes-256-ecb aes-128-ofb aes-192-ofb aes-256-ofb camellia-128-cbc camellia-128-cfb camellia-128-cfb1 amellia-128-cfb8 camellia-128-ecb camellia-128-ofb camellia-192-cbc camellia-192-cfb camellia-192-cfb1 camellia-192-cfb8 camellia-192-ecb camellia-192-ofb camellia-256-cbc camellia-256-cfb camellia-256-cfb1 camellia-256-cfb8 camellia-256-ecb camellia-256-ofb camellia128 camellia192 camellia256)
#
# Repositories trees
# ------------------
BASE_DIR=../data
DLOAD_DIR=$BASE_DIR/downloads
REPO_DIR=$BASE_DIR/repo
SAMPLES_DIR=$BASE_DIR/samples
URLS_DIR=$BASE_DIR/urls

DLOAD_GOVDOCS_DIR=$DLOAD_DIR/govdocs
DLOAD_OPENBSD_DIR=$DLOAD_DIR/openbsd
DLOAD_FIRMWARE_DIR=$DLOAD_DIR/firmware

INIF_SAMPLES_DIR=$SAMPLES_DIR/initial_files
IMGF_SAMPLES_DIR=$SAMPLES_DIR/image_files
FSYS_SAMPLES_DIR=$SAMPLES_DIR/filesystems
FIWR_SAMPLES_DIR=$SAMPLES_DIR/firmwares
MANL_SAMPLES_DIR=$SAMPLES_DIR/manuals_and_notes

PTXT_DIR=$REPO_DIR/plain-text
FBIN_DIR=$REPO_DIR/full-binary
BHEX_DIR=$REPO_DIR/ascii-binary
BDOC_DIR=$REPO_DIR/binary-docs
FSYS_DIR=$REPO_DIR/filesystems
ARVE_DIR=$REPO_DIR/archives
CRYP_DIR=$REPO_DIR/encrypted

#
# URL files
# ---------
URL_OPENBSD_PKG="openbsd-6.1-pkgs-"
URL_GOVDOCS="govdocs1-archives.txt"
URL_FIRMWARE="firmware-urls-1.0.txt"
#
# Options and flags
# -----------------
DEFAULT_GOVDOCS_PKG_DL=1
DEFAULT_OPENBSD_PKG_DL=10
DEFAULT_FIRMWARES_DL=1

DEFAULT_PT_COLL_SIZE=20
DEFAULT_BD_COLL_SIZE=20
DEFAULT_FB_COLL_SIZE=20
DEFAULT_AB_COLL_SIZE=20
DEFAULT_FS_COLL_SIZE=10
DEFAULT_CRYPTO_COLL_SIZE=10
DEFAULT_ARCHIVE_COLL_SIZE=10

DEFAULT_UNCOMPRESSED_CNT=10
DEFAULT_COMPRESSED_CNT=10
DEFAULT_ENCRYPTED_CNT=10

MAX_FILES_FSYS=10

SKIP_CREATE_TREE=1
SKIP_DL_GOVDOCS=1
SKIP_DL_OPENBSD=1
SKIP_DL_FIRMWARE=1

SKIP_PT_COLL=1
SKIP_BD_COLL=1
SKIP_FB_COLL=1
SKIP_AB_COLL=1
SKIP_FS_COLL=1
SKIP_CRYPTO_COLL=0
SKIP_ARCHIVE_COLL=0
SKIP_UCE_SAMPLE=0
#
# Programs and subscripts
# -----------------------
HEX_SCRIPT=./rehex.py
#
# //////////////////////////////////////////////////////////////////////////////
# Functions
# //////////////////////////////////////////////////////////////////////////////
#
# Print usage of the script
# -------------------------
function usage
{
    echo "usage: $0"
}
#
# Install a package as needed.
# ----------------------------
function install_pkg
{
	PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $1 |grep "install ok installed")
	if [ "" == "$PKG_OK" ]; then
	  echo "[=] Installing package '$1'..."
	  sudo apt-get --force-yes --yes install $1 &> $LOG_FILE
	fi
}
#
# Delete all files in the downloads
# directory.
# ---------------------------------
function delete_downloads
{
	if [ -e $DLOAD_DIR ]; then
		rm -rf $DLOAD_DIR/*
		echo "[+] All files in $DLOAD_DIR deleted."
	else
		echo "[-] Directory '$DLOAD_DIR' does not exist."
	fi
}
#
# Delete all files in the samples
# directory.
# ---------------------------------
function delete_samples
{
	if [ -e $SAMPLES_DIR ]; then
		rm -rf $SAMPLES_DIR/*
		echo "[+] All files in $SAMPLES_DIR deleted."
	else
		echo "[-] Directory '$SAMPLES_DIR' does not exist."
	fi
}
#
# Recursively all directories and files in the
# repository directory.
# --------------------------------------------
function delete_repos
{
	if [ -e $REPO_DIR ]; then
		echo -n "[!] Attention: continuing this operation will delete ALL files in $REPO_DIR! [Y/n] "
		read -n 1 ans
		if [ ans == "Y" ]; then
			rm -rf $REPO_DIR
			echo "[+] Operation completed."
		else
			echo "[=] Operation cancelled."
		fi
	else
		echo "[-] No such directory found: '$REPO_DIR'."
	fi
}
#
# Creates the directory tree for collections
# and repositories of files.
# ------------------------------------------
function create_resyst_tree
{
	echo "[=] Creating data directory tree..."
	mkdir -p $DLOAD_DIR
	mkdir -p $REPO_DIR
	mkdir -p $SAMPLES_DIR
	mkdir -p $URLS_DIR
	mkdir -p $RESULTS_DIR
	
	mkdir -p $INIF_SAMPLES_DIR
	mkdir -p $IMGF_SAMPLES_DIR
	mkdir -p $FSYS_SAMPLES_DIR
	mkdir -p $FIWR_SAMPLES_DIR
	mkdir -p $MANL_SAMPLES_DIR
	
	mkdir -p $GOVDOCS_DIR
	mkdir -p $WEB_DIR
	
	mkdir -p $PTXT_DIR
	mkdir -p $FBIN_DIR
	mkdir -p $BHEX_DIR
	mkdir -p $BDOC_DIR
	mkdir -p $ARVE_DIR
	mkdir -p $CRYP_DIR
	
	mkdir -p $UNCP_DIR
	mkdir -p $COMP_DIR
	mkdir -p $ENCR_DIR
	
	echo "[+] Data directory tree successfully created at $BASE_DIR."
}
#
# Downloads GovDocs packages
# --------------------------
function dl_govdocs_pkgs
{
	N=$1

	DROP_DIR=$DLOAD_GOVDOCS_DIR/
	if [ ! -e $DROP_DIR ]; then
		mkdir -p $DROP_DIR
		echo "[+] Created destination directory '$DROP_DIR'."
	fi

	FILE="$URLS_DIR/$URL_GOVDOCS"
	
	if [ ! -e $FILE ]; then
		echo "[-] Could not find GovDocs URL list: $FILE."
	else
		echo "[=] Downloading $N $A file(s) listed in $FILE"
		cat $FILE | sort -R | tail -$N | while read URL; do
			URL=${URL//[$'\t\r\n']}
			URL_FILE=${URL##*/}
			PGK_NO=${URL_FILE%.*}
			if [ ! -e $DLOAD_GOVDOCS_DIR/$URL_FILE ]; then
				echo "[>]	$URL_FILE"
				wget -nH -nd --tries=5 --mirror -o dropper.log $URL -P $DLOAD_GOVDOCS_DIR &> /dev/null
				unzip $DLOAD_GOVDOCS_DIR/$URL_FILE  -d $DROP_DIR/
				rm -rf $DLOAD_GOVDOCS_DIR/$URL_FILE
			else
				echo "[-] '$DLOAD_GOVDOCS_DIR/$URL_FILE' already exists."
			fi
		done
		
		echo "[+] Download completed."
	fi
}
#
# Downloads random packages from the
# OpenBSD repositories from multiple architectures
# ------------------------------------------------
function dl_openbsd_pkgs
{
	N=$1
	for A in "${ARCH[@]}"; do
		
		DROP_DIR=$DLOAD_OPENBSD_DIR/$A
		if [ ! -e $DROP_DIR ]; then
			mkdir -p $DROP_DIR
			echo "[+] Created destination directory '$DROP_DIR'."
		fi

		FILE="$URLS_DIR/$URL_OPENBSD_PKG$A.txt"
		
		if [ ! -e $FILE ]; then
			echo "[-] Could not find OpenBSD URL list: $FILE."
		else
			echo "[=] Downloading $N $A binary file(s) listed in $FILE"
			cat $FILE | sort -R | tail -$N | while read URL; do
				URL=${URL//[$'\t\r\n']}
				URL_FILE=${URL##*/}
				if [ ! -e $DLOAD_OPENBSD_DIR/$URL_FILE ]; then
					echo "[>]	$URL_FILE"
					wget -nH -nd --tries=5 --mirror -o dropper.log $URL -P $DLOAD_OPENBSD_DIR &> /dev/null
					tar -C $DROP_DIR -zxvf $DLOAD_OPENBSD_DIR/$URL_FILE bin
					tar -C $DROP_DIR -zxvf $DLOAD_OPENBSD_DIR/$URL_FILE lib
					rm -rf $DLOAD_OPENBSD_DIR/$URL_FILE
				else
					echo "[-] File '$DLOAD_OPENBSD_DIR/$URL_FILE' already exists."
				fi
			done
			
			echo "[+] Download completed."
		fi
	done
}

#
# Downloads random packages from the
# OpenBSD repositories from multiple architectures
# ------------------------------------------------
function dl_firmwares
{
	N=$1

	DROP_DIR=$DLOAD_FIRMWARE_DIR
	if [ ! -e $DROP_DIR ]; then
		mkdir -p $DROP_DIR
		echo "[+] Created destination directory '$DROP_DIR'."
	fi

	FILE="$URLS_DIR/$URL_FIRMWARE"
	
	if [ ! -e $FILE ]; then
		echo "[-] Could not find firmware URL list: $FILE."
	else
		echo "[=] Downloading $N $A binary file(s) listed in $FILE"
		cat $FILE | sort -R | tail -$N | while read URL; do
			URL=${URL//[$'\t\r\n']}
			URL_FILE=${URL##*/}
			if [ ! -e $DLOAD_FIRMWARE_DIR/$URL_FILE ]; then
				echo "[>]	$URL_FILE"
				wget -nH -nd --tries=5 --mirror -o dropper.log $URL -P $DLOAD_FIRMWARE_DIR &> /dev/null
			else
				echo "[-] File '$DLOAD_FIRMWARE_DIR/$URL_FILE' already exists."
			fi
		done

		echo "[+] Download completed."
	fi
}
#
# Creates the plain-text file 
# collection
# ---------------------------
function create_pt_collection
{
	N=$1
	echo "[=] Creating plain-text file collection (N=$N)..."
	if [ -e $DLOAD_GOVDOCS_DIR ]; then
		find $DLOAD_GOVDOCS_DIR -regextype posix-egrep -regex ".*\.(txt|xml|css|js|rtf|html|1st)$" -type f | sort -R | tail -$N | while read FILE; do
			echo "[>] 	$FILE ..."
			cp $FILE $PTXT_DIR &> /$LOG_FILE
		done
	else
		echo "[-] Could not find '$DLOAD_GOVDOCS_DIR'."
	fi
}
#
# Creates the binary document file 
# collection
# ---------------------------
function create_bd_collection
{
	N=$1
	echo "[=] Creating binary documents file collection (N=$N)..."
	if [ -e $DLOAD_GOVDOCS_DIR ]; then
		find $DLOAD_GOVDOCS_DIR -regextype posix-egrep -regex ".*\.(doc|ppt|pdf|xls)$" -type f | sort -R | tail -$N | while read FILE; do
			echo "[>] 	$FILE ..."
			cp $FILE $BDOC_DIR &> /$LOG_FILE
		done
	else
		echo "[-] Could not find '$DLOAD_GOVDOCS_DIR'."
	fi
}
#
# Creates the full binary file 
# collection
# ---------------------------
function create_fb_collection
{
	N=$1
	for A in "${ARCH[@]}"; do
		DROP_DIR=$DLOAD_OPENBSD_DIR/$A
		DST_DIR=$FBIN_DIR/$A
		
		if [ ! -e $DST_DIR ]; then
			mkdir -p $DST_DIR
		fi
		
		echo "[=] Creating $A binary file collection (N=$N)..."
		if [ -e $DROP_DIR ]; then
			find $DROP_DIR -type f | sort -R | tail -$N | while read FILE; do
				echo "[>] 	$FILE ..."
				cp $FILE $DST_DIR &> /$LOG_FILE
			done
		else
			echo "[-] Could not find '$DLOAD_GOVDOCS_DIR'."
		fi
	done
}
#
# Generates a collection of ASCII-formated binary
# files from the full-binary collection.
# -----------------------------------------------
function generate_ab_collection
{
	N=$1

	echo "[=] Generating $N HEX files..."
	find $FBIN_DIR -type f -exec file -i '{}' \; | grep 'charset=binary' | cut -d: -f1 | sort -R | tail -$N | while read FILE; do
		HEX_TYPE=${HEX_FORMATS[$RANDOM % ${#HEX_FORMATS[@]}]}
		OUT_DIR="$BHEX_DIR/$HEXTYPE"
		if [ ! -e $OUT_DIR ]; then
			mkdir -p $OUT_DIR
		fi
		OUT_FILE="$OUT_DIR/${FILE##*/}.$HEX_TYPE"
		echo "[>]	$OUT_FILE"
		python3 $HEX_SCRIPT -b $FILE -f $HEX_TYPE -o $OUT_FILE &> /$LOG_FILE
	done
}
#
# Generate a CRAMFS image file
# ----------------------------
function generate_cramfs
{
	N=$1
	TDIR=`mktemp -d -t resyst.XXXX`
	IMAGE_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)
	DST_DIR=$FSYS_DIR/cramfs
	OUT_FILE=$DST_DIR/$IMAGE_NAME.cramfs
	
	find $REPO_DIR -type f | sort -R | tail -$N | while read FILE; do
		cp $FILE $TDIR
	done
	
	mkfs.cramfs $TDIR $OUT_FILE &> $LOG_FILE
	echo "[>]	$OUT_FILE"
	rm -rf $TDIR
}
#
# Generate a Squash image file
# ----------------------------
function generate_squash
{
	N=$1
	TDIR=`mktemp -d -t resyst.XXXX`
	IMAGE_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)
	COMP=(gzip lzma lzo lz4 xz)
	COMP_TYPE=${COMP[$RANDOM % ${#COMP[@]}]}
	DST_DIR=$FSYS_DIR/squashfs
	OUT_FILE=$DST_DIR/$IMAGE_NAME.sqsh
	
	find $REPO_DIR -type f | sort -R | tail -$N | while read FILE; do
		cp $FILE $TDIR
	done
	
	mksquashfs $TDIR/* OUT_FILE -comp $COMP_TYPE &> $LOG_FILE
	echo "[>]	$OUT_FILE"
	rm -rf $TDIR
}
#
# Generates a JFFS2 filesystems
# -----------------------------
function generate_jffs2
{
	N=$1
	TDIR=`mktemp -d -t resyst.XXXX`
	IMAGE_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)
	DST_DIR=$FSYS_DIR/jffs2
	OUT_FILE=$DST_DIR/$IMAGE_NAME.jffs2

	find $REPO_DIR -type f | sort -R | tail -$N | while read FILE; do
		cp $FILE $TDIR
	done
	
	mkfs.jffs2 --root $TDIR -o $OUT_FILE &> $LOG_FILE
	echo "[>]	$OUT_FILE"
	rm -rf $TDIR
}
#
# sqsh cramfs jffs2
function generate_fs_collection
{
	N=$1
	echo "[=] Creating $N file system image(s)..."
	for i in $(seq 1 $N); do
		FS_TYPE=${FSYS[$RANDOM % ${#FSYS[@]}]}
		NB_FILES=$((1 + RANDOM % $MAX_FILES_FSYS))
		case $FS_TYPE in 
			"cramfs")
				generate_cramfs $NB_FILES
				;;
			"jffs2")
				generate_jffs2 $NB_FILES
				;;
			"sqsh")
				generate_squash $NB_FILES
				;;
			*)
				break
				;;
		esac
	done
}
#
# Generate a collection of 
# encrypted files
# -------------------------
function generate_crypto_collection
{
	N=$1
	echo "[=] Generating $N encrypted file(s)..."
	
	if [ ! -e $CRYP_DIR ]; then
		mkdir -p $CRYP_DIR
	fi
	
	find $REPO_DIR -type f | sort -R | tail -$N | while read FILE; do
		CRYPTO_TYPE=${CRYPTOS[$RANDOM % ${#CRYPTOS[@]}]}
		FILENAME=$(basename "$FILE")
		CRYPTO_FILE=$CRYP_DIR/$FILENAME.enc
		PASSCODE=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
		if [ ! -e $CRYPTO_FILE ]; then
			echo "[>]	$CRYPTO_FILE using $CRYPTO_TYPE."
			openssl enc -in $FILE -$CRYPTO_TYPE -out $CRYPTO_FILE -pass pass:$PASSCODE &> $LOG_FILE
		fi
	done
}
#
# Generates a collection of compressed
# files.
# -------------------------------------
function generate_compressed_collection
{
	N=$1
	echo "[=] Generating $N compressed file(s)..."
	
	if [ ! -e $ARVE_DIR ]; then
		mkdir -p $ARVE_DIR
	fi
	
	find $REPO_DIR -type f | sort -R | tail -$N | while read FILE; do	
		ARCHIVE_TYPE=${ARCHIVES[$RANDOM % ${#ARCHIVES[@]}]}
		FILENAME=$(basename "$FILE")
		ARCHIVE_FILE=$ARVE_DIR/$FILENAME$ARCHIVE_TYPE
		if [ ! -e $ARCHIVE_FILE ]; then
			echo "[>]	$ARCHIVE_FILE"
			atool -a $ARCHIVE_FILE $FILE &> $LOG_FILE
		fi
	done
}

function generate_uce_sample
{
	N_U=$1
	N_C=$2
	N_E=$3
	
	echo "[=] Create sample for U/C/E classification..."
	echo "[=] Copying $N_U uncompressed file(s)..."
	find $FBIN_DIR -type f | sort -R | tail -$N_U | while read FILE; do
		FILENAME=$(basename "$FILE")
		DST_FILE=$INIF_SAMPLES_DIR/$FILENAME.uncompressed

		if [ ! -e $DST_FILE ]; then
			echo "[>]	$DST_FILE"
			cp $FILE $DST_FILE
		fi
	done
	
	echo "[=] Copying $N_C compressed file(s)..."
	find $ARVE_DIR -type f | sort -R | tail -$N_C | while read FILE; do
		FILENAME=$(basename "$FILE")
		DST_FILE=$INIF_SAMPLES_DIR/$FILENAME.compressed

		if [ ! -e $DST_FILE ]; then
			echo "[>]	$DST_FILE"
			cp $FILE $DST_FILE
		fi
	done	
	
	echo "[=] Copying $N_E encrypted file(s)..."
	find $CRYP_DIR -type f | sort -R | tail -$N_E | while read FILE; do
		FILENAME=$(basename "$FILE")
		DST_FILE=$INIF_SAMPLES_DIR/$FILENAME.encrypted

		if [ ! -e $DST_FILE ]; then
			echo "[>]	$DST_FILE"
			cp $FILE $DST_FILE
		fi
	done	
}
#
# //////////////////////////////////////////////////////////////////////////////
#
# Main
# ------------
clear

if [ ! -e ./$URL_ARCHIVE ]; then
	echo "[-] Could not find directory containing URL lists: $URL_ARCHIVE."
	exit 1
else
	if [ $SKIP_CREATE_TREE -eq 0 ]; then
		rm -rf $BASE_DIR
		create_resyst_tree
		unzip $URL_ARCHIVE -d $URLS_DIR 
	fi
	
	if [ $SKIP_DL_GOVDOCS -eq 0 ]; then
		dl_govdocs_pkgs $DEFAULT_GOVDOCS_PKG_DL
	fi
	
	if [ $SKIP_DL_OPENBSD -eq 0 ]; then
		dl_openbsd_pkgs $DEFAULT_OPENBSD_PKG_DL
	fi
	
	if [ $SKIP_DL_FIRMWARE -eq 0 ]; then
		dl_firmwares $DEFAULT_FIRMWARES_DL
	fi
	
	if [ $SKIP_PT_COLL -eq 0 ]; then
		create_pt_collection $DEFAULT_PT_COLL_SIZE
	fi
	
	if [ $SKIP_BD_COLL -eq 0 ]; then
		create_bd_collection $DEFAULT_BD_COLL_SIZE
	fi
	
	if [ $SKIP_FB_COLL -eq 0 ]; then
		create_fb_collection $DEFAULT_FB_COLL_SIZE
	fi
	
	if [ $SKIP_AB_COLL -eq 0 ]; then
		generate_ab_collection $DEFAULT_AB_COLL_SIZE
	fi
	
	if [ $SKIP_FS_COLL -eq 0 ]; then
		generate_fs_collection $DEFAULT_FS_COLL_SIZE
	fi
	
	if [ $SKIP_ARCHIVE_COLL -eq 0 ]; then
		install_pkg lzip
		install_pkg bzip2
		install_pkg lzop
		install_pkg lzma
		install_pkg zip
		install_pkg rar
		install_pkg arj
		install_pkg unace
		install_pkg arc
		install_pkg nomarch
		install_pkg p7zip
		generate_compressed_collection $DEFAULT_ARCHIVE_COLL_SIZE
	fi
	
	if [ $SKIP_CRYPTO_COLL -eq 0 ]; then
		generate_crypto_collection $DEFAULT_CRYPTO_COLL_SIZE
	fi
	
	if [ $SKIP_UCE_SAMPLE -eq 0 ]; then
		generate_uce_sample $DEFAULT_UNCOMPRESSED_CNT $DEFAULT_COMPRESSED_CNT $DEFAULT_ENCRYPTED_CNT
	fi
fi
