#!/bin/bash

N=300
C_U=100
C_C=200
C_E=70
SRC=./data/training/govdocs
DST=./data/training/obfuscated
TEST=./data/testing/uce_sample
RESYST=../resyst/ReSyst/resyst/main.py

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

