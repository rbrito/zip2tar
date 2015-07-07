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


version_info = (0, 4)
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


class Tar(object):
    def __init__(self, file_name, typ, **kw):
        """
        create a (compressed) tar file for writing in-memory objects
        typ should be from 'gz', 'bz2', 'xz'
        """
        self._file_name = file_name
        self._typ = 'w:' if typ is None else 'w:' + typ
        self._kw = kw
        self._md5 = None
        self._md5_data = []
        self._fp = None
        self._dts = None
        self._xz = None

    @property
    def fp(self):
        if self._fp is None:
            if self._typ == 'w:xz' and sys.version_info < (3, ):
                import lzma

                self._xz = xz = lzma.LZMAFile(self._file_name, 'w')
                self._fp = tarfile.open(mode='w:', fileobj=xz, **self._kw)
            else:
                self._fp = tarfile.open(self._file_name, self._typ, **self._kw)
        return self._fp

    @property
    def dts(self):
        return self._dts

    @dts.setter
    def dts(self, val):
        self._dts = val

    @property
    def md5(self):
        return self._md5

    def compression_level(self, val):
        if self._typ in ['w:bz2', 'w:gz']:
            self._kw['compresslevel'] = val

    @md5.setter
    def md5(self, val):
        self._md5 = 'sum.md5' if val is True else val

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_inst, exc_tb):
        if self._fp:
            if self._md5_data:
                import io
                buf = io.BytesIO()
                buf.write(''.join(self._md5_data).encode('utf-8'))
                size = buf.tell()
                buf.seek(0)
                self.write_one_obj(self._md5, size, buf)
            self._fp.close()
            self._fp = None
        if self._xz:
            self._xz.close()
            self._xz = None

    def write_one_obj(self, file_name, data_len, data_obj, date_time=None):
        tar_info = tarfile.TarInfo(name=file_name)
        if file_name is not self._md5 and self._md5 and file_name == self._md5:
            raise NotImplementedError
        tar_info.size = data_len
        if self.dts is 0:
            mtime = None
        elif isinstance(self.dts, datetime.datetime):
            mtime = time.mktime(self.dts.utctimetuple())
            if mtime < 0.0:
                mtime = None
        elif date_time is None:
            mtime = None
        elif self.dts is None:
            mtime = time.mktime(tuple(list(date_time) +
                                      [-1, -1, -1]))
        if mtime is not None:
            tar_info.mtime = mtime
        if file_name is not self._md5 and self._md5:
            # test on data_obj.seek(0) to not create BytesIO is supported?
            import hashlib
            import io
            # have to deal with reading data_obj twice
            buf = io.BytesIO(data_obj.read())
            m = hashlib.md5()
            m.update(buf.read())
            buf.seek(0)
            self._md5_data.append(
                '{}  {}\n'.format(m.hexdigest(), file_name))
            data_obj = buf
        self.fp.addfile(tarinfo=tar_info, fileobj=data_obj)

    def convert_zip(self, in_file_name):
        with ZipFile(in_file_name) as zipf:
            for zip_info in zipf.infolist():
                self.write_one_obj(
                    zip_info.filename,
                    zip_info.file_size,
                    zipf.open(zip_info.filename),
                    zip_info.date_time,
                )


def zip2tar(in_file_name, out_file_name, typ=None, lvl=9):
    """
    Conversion of zip to tar in memory.
    typ should be from 'gz', 'bz2', 'xz'
    lvl is the compression level for 'gz' and 'bz2' lower it for higher speed
    """
    # typ = 'w:' if typ is None else 'w:' + typ
    kw = {}
    if lvl is not None:
        kw['compresslevel'] = lvl
    with Tar(out_file_name, typ=typ, **kw) as tar:
        tar.convert_zip(in_file_name)


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
    if sys.version_info >= (2, 7) and args.xz:
        compress = 'xz'
    elif args.bz2:
        compress = 'bz2'
    elif args.gz:
        compress = 'gz'
    else:
        compress = None
    compress_extension = '.' + compress if compress else ''
    out_file_name = args.tar_file_name
    if not out_file_name:
        out_file_name = args.filename.replace(
            '.zip', '.tar' + compress_extension)
    # dts = datetime.datetime(2011, 10, 2, 16, 45, 0)
    with Tar(out_file_name, compress) as tarf:
        tarf.compression_level(args.compression_level)
        if args.no_datetime:
            tarf.dts = 0
        if args.md5:
            tarf.md5 = args.md5
        tarf.convert_zip(args.filename)

    # res = zip2tar(args.filename, out_file_name, compress)
    sys.exit(0)  # if res is None -> 0 as exit

if __name__ == '__main__':
    main()
