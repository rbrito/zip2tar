
UTILNAME:=zip2tar
PKGNAME:=ruamel.zip2tar
VERSION:=$(shell python setup.py --version)
REGEN:=/home/bin/ruamel_util_new util Zip2Tar -c --published --skip-hg \
   --no-config

include ~/.config/ruamel_util_new/Makefile.inc

clean:	clean_common
#	rm -rf build .tox $(PKGNAME).egg-info/ README.pdf
#	find . -name "*.pyc" -exec rm {} +
