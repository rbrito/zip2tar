# coding: utf-8

# The MIT License (MIT)
#
# Copyright (c) 2013-2015 Anthon van der Neut, Ruamel bvba
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import print_function


def _convert_version(tup):
    """Create a PEP 386 pseudo-format conformant string from tuple tup."""
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


version_info = (0, 3, 3)
__version__ = _convert_version(version_info)

del _convert_version

import sys
from zipfile import ZipFile
import tarfile
import time
import argparse
import datetime


# < from ruamel.std.argparse._action.count import CountAction
class CountAction(argparse.Action):
    """argparse action for counting up and down

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action=CountAction,
                        const=1, nargs=0)
    parser.add_argument('--quiet', '-q', action=CountAction, dest='verbose',
            const=-1, nargs=0)
    """
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            val = getattr(namespace, self.dest) + self.const
        except TypeError:  # probably None
            val = self.const
        setattr(namespace, self.dest, val)


def zip2tar(in_file_name, out_file_name, typ=None, lvl=9, dts=None,
            md5=None):
    """
    Conversion of zip to tar in memory.
    typ should be from 'gz', 'bz2', 'xz' (3.4)
    """
    md5_sum_filename = 'sum.md5'

    def write_one(zip_info, tar_file, tarf, md5=None):
        tar_info = tar_file.TarInfo(name=zip_info.filename)
        if md5 and zip_info.filename == md5_sum_filename:
            raise NotImplementedError
        tar_info.size = zip_info.file_size
        if dts is None:
            mtime = time.mktime(tuple(list(zip_info.date_time) +
                                      [-1, -1, -1]))
        elif dts is 0:
            mtime = None
        elif isinstance(dts, datetime.datetime):
            mtime = time.mktime(dts.utctimetuple())
            if mtime < 0.0:
                mtime = None
        if mtime is not None:
            tar_info.mtime = mtime
        tarf.addfile(
            tarinfo=tar_info,
            fileobj=zipf.open(zip_info.filename)
        )
        if md5 is not None:
            import hashlib
            m = hashlib.md5()
            m.update(zipf.open(zip_info.filename).read())
            md5.append('{}  {}\n'.format(m.hexdigest(), zip_info.filename))

    def add_md5(tar_file, tarf, md5_data):
        if not md5_data:
            return
        import io
        tar_info = tar_file.TarInfo(name=md5_sum_filename)
        print ('------------------------------here')
        buf = io.BytesIO()
        buf.write(''.join(md5_data).encode('utf-8'))
        tar_info.size = buf.tell()
        buf.seek(0)
        tarf.addfile(
            tarinfo=tar_info,
            fileobj=buf,
        )

    typ = 'w:' if typ is None else 'w:' + typ
    kw = {}
    if lvl is not None:
        kw['compresslevel'] = lvl
    md5_data = [] if md5 else None
    with ZipFile(in_file_name) as zipf:
        if typ == 'w:xz' and sys.version_info < (3, ):
            import lzma
            import contextlib

            with contextlib.closing(lzma.LZMAFile(out_file_name, 'w')) as xz:
                with tarfile.open(mode='w:', fileobj=xz) as tarf:
                    for zip_info in zipf.infolist():
                        write_one(zip_info, tarfile, tarf, md5=md5_data)
        else:
            with tarfile.open(out_file_name, typ, **kw) as tarf:
                for zip_info in zipf.infolist():
                    write_one(zip_info, tarfile, tarf, md5_data)
                add_md5(tarfile, tarf, md5_data)


def main():
    parser = argparse.ArgumentParser(
        description="in-memory zip to tar convertor")
    parser.add_argument('--verbose', '-v', help='increase verbosity level',
                        action=CountAction, const=1, nargs=0)
    if sys.version_info >= (2, 7):
        parser.add_argument(
            '--xz', action='store_true',
            help='write xz compressed tar file')
    parser.add_argument(
        '--bz2', action='store_true',
        help='write bzip2 compressed tar file')
    parser.add_argument(
        '--gz', action='store_true',
        help='write gzip compressed tar file')
    parser.add_argument('--compression-level', type=int, default=9)
    parser.add_argument(
        '--no-datetime', action="store_true",
        help="don't take datetime for files from zip -> 1970-01-01")
    parser.add_argument(
        '--tar-file-name', metavar='NAME',
        help='set tar file name (normally derived from .zip)')
    parser.add_argument(
        '--md5', action="store_true",
        help="add a 'sum.md5' file (cannot already be in the zip)")
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('filename')
    args = parser.parse_args()
    lvl = args.compression_level
    if sys.version_info >= (2, 7) and args.xz:
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
    dts = None
    if args.no_datetime:
        dts = 0
    # dts = datetime.datetime(2011, 10, 2, 16, 45, 0)
    res = zip2tar(args.filename, out_file_name,
                  compress, lvl, dts=dts, md5=args.md5)
    sys.exit(res)  # if res is None -> 0 as exit

if __name__ == '__main__':
    main()
