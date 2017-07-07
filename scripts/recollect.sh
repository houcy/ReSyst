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

# //////////////////////////////////////////////////////////////////////////////
# Variables and parameters
# //////////////////////////////////////////////////////////////////////////////
#
# Log file
# --------
LOG_FILE="recollect.log"
#
# Repositories trees
# ------------------
BASE_DIR=`pwd`
DLOAD_DIR=$BASE_DIR/downloads
REPO_DIR=$BASE_DIR/repo
SAMPLES_DIR=$BASE_DIR/samples
URLS_DIR=$BASE_DIR/urls

INIF_SAMPLES_DIR=$SAMPLES_DIR/initial_files
IMGF_SAMPLES_DIR=$SAMPLES_DIR/image_files
FSYS_SAMPLES_DIR=$SAMPLES_DIR/filesystems
FIWR_SAMPLES_DIR=$SAMPLES_DIR/firmwares
MANL_SAMPLES_DIR=$SAMPLES_DIR/manuals

GOVDOCS_DIR=$BASE_DIR/repo/govdocs
WEB_DIR=$REPO_DIR/plain-text/web

PTXT_DIR=$REPO_DIR/plain-text
FBIN_DIR=$REPO_DIR/full-binary
BHEX_DIR=$REPO_DIR/ascii-binary
BDOC_DIR=$REPO_DIR/binary-docs

UNCP_DIR=$REPO_DIR/uncompressed
COMP_DIR=$REPO_DIR/compressed
ENCR_DIR=$REPO_DIR/encrypted

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
	
	mkdir -p $UNCP_DIR
	mkdir -p $COMP_DIR
	mkdir -p $ENCR_DIR
	
	echo "[+] Data directory tree successfully created at $BASE_DIR."
}

#
# Displays the main menu
# ----------------------
function display_main_menu
{
	local OPT=""
	while [ "$OPT" != "0" ]; do
		clear
		echo "ReSyst 1.0.0"
		echo "Main Menu:"
		echo "--------------------"
		echo "[1] Repositories    "
		echo "[2] Downloads       "
		echo "[3] Samples         "
		echo "[4] Training        "
		echo "[5] Testing         "
		echo "[6] Analyze         "
		echo ""
		echo "[0] Exit            "
		echo ""
		echo "--------------------"
		echo -n "[<] "
		read -n 1 OPT
		
		if [ $OPT == "1" ]; then
			display_repo_menu
		elif [ $OPT == "2" ]; then
			display_dload_menu
		fi
	done
}

function display_repo_menu
{
	local OPT=""
	while [ "$OPT" != "0" ]; do
		clear
		echo "ReSyst 1.0.0"
		echo "Repositories Menu:"
		echo "--------------------"
		echo "[1] Create Repos    "
		echo "[2] Clear Repos     "
		echo "[3] Clear Samples   "
		echo "[4] Clear Downloads "
		echo ""
		echo "[0] Back            "
		echo ""
		echo "--------------------"
		echo ""
		echo -n "[<] "
		read -n 1 OPT
		
		if [ $OPT == "1" ]; then
			create_resyst_tree
		elif [ $OPT == "2" ]; then 
			delete_repos
		elif [ $OPT == "3" ]; then 			
			delete_samples
		elif [ $OPT == "4" ]; then
			delete_downloads
		fi
	done
}

function display_dload_menu
{
	local OPT=""
	while [ $OPT != "0" ]; do
		clear
		echo "ReSyst 1.0.0"
		echo "Downloads Menu:"
		echo "--------------------"
		echo "[1] GovDocs         "
		echo "[2] OpenBSD Packages"
		echo ""
		echo "[0] Back            "
		echo ""
		echo "--------------------"
		echo ""
		echo -n "[<] "
		read -n 1 OPT
		echo ""
	done
}

# //////////////////////////////////////////////////////////////////////////////
#
# Main
# ------------
display_main_menu
clear