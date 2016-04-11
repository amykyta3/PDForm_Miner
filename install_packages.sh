#! /bin/bash

# Check if root
if [ "$(id -u)" != "0" ] ; then
	echo "Please run this as administrator (sudo)"
	exit 1
fi

pip3 install pdfminer3k
pip3 install pyexcel
pip3 install pyexcel-ods3
pip3 install pyexcel-xlsx
pip3 install pyexcel-xls
