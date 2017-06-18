#!/bin/bash

##### Constants


##### Variables
SRC_DIR=0
DST_DIR=0
N=0
COMPRESS=0
ENCRYPT=0
ARCHIVES=(.zip .tar.gz .bz2 .lzip .lzop .lzma .rar .lha .ace .arj .cpio .arc .7z)
CRYPTOS=(bf-cbc bf bf-cfb bf-ecb bf-ofb cast-cbc cast cast5-cbc cast5-cfb cast5-ecb cast5-ofb des-cbc des des-cfb des-ofb des-ecb des-ede-cbc des-ede des-ede-cfb des-ede-ofb des-ede3-cbc des-ede3 des3 des-ede3-cfb des-ede3-ofb desx rc2-cbc rc2 rc2-cfb rc2-ecb rc2-ofb rc2-64-cbc rc2-40-cbc rc4 rc4-40 aes-128-cbc aes-192-cbc aes-256-cbc aes-128-cfb aes-192-cfb aes-256-cfb aes-128-cfb1 aes-192-cfb1 aes-256-cfb1 aes-128-cfb8 aes-192-cfb8 aes-256-cfb8 aes-128-ecb aes-192-ecb aes-256-ecb aes-128-ofb aes-192-ofb aes-256-ofb camellia-128-cbc camellia-128-cfb camellia-128-cfb1 amellia-128-cfb8 camellia-128-ecb camellia-128-ofb camellia-192-cbc camellia-192-cfb camellia-192-cfb1 camellia-192-cfb8 camellia-192-ecb camellia-192-ofb camellia-256-cbc camellia-256-cfb camellia-256-cfb1 camellia-256-cfb8 camellia-256-ecb camellia-256-ofb camellia128 camellia192 camellia256)

##### Functions
function usage
{
    echo "usage: $0 [[-s|--src] <directory>] [[-d|--dest] <directory>] [-c <count>] [-z|--zip] [-e|--encrypt]"
}

function install_pkg
{
	PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $1 |grep "install ok installed")
	if [ "" == "$PKG_OK" ]; then
	  echo "[=] Installing package '$1'..."
	  sudo apt-get --force-yes --yes install $1 &> /dev/null
	fi
}

##### Main

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

while [ "$1" != "" ]; do
    case $1 in
        -s | --src  )           shift
                                SRC_DIR=$1
                                ;;
        -d | --dest )    		shift
								DST_DIR=$1
                                ;;
        -c | --count)    		shift
								N=$1
                                ;;
        -z | --zip  )    		COMPRESS=1
                                ;;
        -e | --encrypt)    		ENCRYPT=1
                                ;;									
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

mkdir -p $DST_DIR

find $SRC_DIR -type f | sort -R | tail -$N | while read FILE; do
	FILENAME=$(basename "$FILE")

	if [ $COMPRESS -eq 1 ]; then
		ARCHIVE_TYPE=${ARCHIVES[$RANDOM % ${#ARCHIVES[@]}]}
		ARCHIVE_FILE=$DST_DIR/$FILENAME$ARCHIVE_TYPE
		echo [=] Compressing $FILENAME to $ARCHIVE_FILE
		atool -a $ARCHIVE_FILE $FILE &> /dev/null
	elif [ $ENCRYPT -eq 1 ]; then
		CRYPTO_TYPE=${CRYPTOS[$RANDOM % ${#CRYPTOS[@]}]}
		CRYPTO_FILE=$DST_DIR/$FILENAME.enc
		PASSCODE=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
		echo [=] Encrypting $FILENAME to $CRYPTO_FILE using $CRYPTO_TYPE
		openssl enc -in $FILE -$CRYPTO_TYPE -out $CRYPTO_FILE -pass pass:$PASSCODE &> /dev/null
	else
		DST_FILE=$DST_DIR/$FILENAME
		echo [=] Copying $FILE to $DST_FILE
		cp $FILE $DST_DIR
	fi
done