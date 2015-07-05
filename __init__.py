# coding: utf-8

from __future__ import print_function


def _convert_version(tup):
    """create a PEP 386 pseudo-format conformant string from tuple tup"""
    ret_val = str(tup[0])  # first is always digit
    next_sep = "."  # separator for next extension, can be "" or "."
    for x in tup[1:]:
        if isinstance(x, int):
            ret_val += next_sep + str(x)
            next_sep = '.'
            continue
        first_letter = x[0].lower()
        next_sep = ''
        if first_letter in 'abcr':
            ret_val += 'rc' if first_letter == 'r' else first_letter
        elif first_letter in 'pd':
            ret_val += '.post' if first_letter == 'p' else '.dev'
    return ret_val


version_info = (0, 2)
__version__ = _convert_version(version_info)

del _convert_version

import sys
from zipfile import ZipFile
import tarfile
import time
import argparse

# < from ruamel.std.argparse._action.count import CountAction
class CountAction(argparse.Action):
    """argparse action for counting up and down

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action=CountAction, const=1, nargs=0)
    parser.add_argument('--quiet', '-q', action=CountAction, dest='verbose',
            const=-1, nargs=0)
    """
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            val = getattr(namespace, self.dest) + self.const
        except TypeError: # probably None
            val = self.const
        setattr(namespace, self.dest, val)


# for python 2.7 you could use contextlib and lzma

def zip2tar(ifn, ofn, typ=None, lvl=9):
    """
    conversion of zip to tar in memory
    typ should be from 'gz', 'bz2', 'xz' (3.4)
    """
    typ = 'w:' if typ is None else 'w:' + typ
    kw = {}
    if lvl is not None:
        kw['compresslevel'] = lvl
    with ZipFile(ifn) as zipf:
        with tarfile.open(ofn, typ, **kw) as tarf:
            for zip_info in zipf.infolist():
                tar_info = tarfile.TarInfo(name=zip_info.filename)
                tar_info.size = zip_info.file_size
                tar_info.mtime = time.mktime(tuple(list(zip_info.date_time) +
                                         [-1, -1, -1]))
                tarf.addfile(
                    tarinfo=tar_info,
                    fileobj=zipf.open(zip_info.filename)
                )


def main():
    parser = argparse.ArgumentParser(
        description="in-memory zip to tar convertor")
    parser.add_argument('--verbose', '-v', help='increase verbosity level',
                        action=CountAction, const=1, nargs=0)
    parser.add_argument('--xz', action='store_true')
    parser.add_argument('--bz2', action='store_true')
    parser.add_argument('--gz', action='store_true')
    parser.add_argument('--compression-level', type=int, default=9)
    parser.add_argument('--tar-file-name')
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('filename')
    args = parser.parse_args()
    lvl = args.compression_level
    if args.xz:
        lvl = None
        compress = 'xz'
    elif args.bz2:
        compress = 'bz2'
    elif args.gz:
        compress = 'gz'
    else:
        lvl = None
        compress = None
    compress_extension = '.' + compress if compress else ''
    out_file_name = args.tar_file_name
    if not out_file_name:
        out_file_name = args.filename.replace(
            '.zip', '.tar' + compress_extension)
    res = zip2tar(args.filename, out_file_name,
                  compress, lvl)
    sys.exit(res) # if res is None -> 0 as exit

if __name__ == '__main__':
    main()

