# coding 'utf-8'

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

import subprocess
from textwrap import dedent

import pytest
# here to quiet flake8
_pytest_major_minor = tuple(map(int, pytest.__version__.split('.', 2)[:2]))
assert _pytest_major_minor >= (2, 7)


def create_zip(td, mp):
    path = td.join('test.zip')
    if not path.exists():
        mp.chdir(td)
        fl = ['abc', 'def', 'ghi']
        for x in fl:
            with open(x, 'w') as fp:
                fp.write(x)
        print(subprocess.check_output(['zip', 'test.zip'] + fl))
    return path


def z2t(zip_file, gzip=False, bzip2=False, xz=False, no_date=False):
    print('z2t ------------------')
    cmd = ['zip2tar']
    if gzip:
        cmd.append('--gz')
        ext = 'tar.gz'
    elif bzip2:
        cmd.append('--bz2')
        ext = 'tar.bz2'
    elif xz:
        cmd.append('--xz')
        ext = 'tar.xz'
    else:
        ext = 'tar'
    if no_date:
        cmd.append('--no-datetime')
    cmd.append(str(zip_file))
    subprocess.check_output(cmd)
    return zip_file.new(ext=ext)


def untar(tar_f):
    return subprocess.check_output(['tar', 'tf', str(tar_f)]).decode('ascii')


class TestZ2T:

    def test_non_comp(self, tmpdir, monkeypatch):
        z = create_zip(tmpdir, monkeypatch)
        t = z2t(z)
        res = untar(t)
        assert res == 'abc\ndef\nghi\n'

    def test_gzip(self, tmpdir, monkeypatch):
        z = create_zip(tmpdir, monkeypatch)
        t = z2t(z, gzip=True)
        res = untar(t)
        assert res == 'abc\ndef\nghi\n'

    def test_bzip2(self, tmpdir, monkeypatch):
        z = create_zip(tmpdir, monkeypatch)
        t = z2t(z, bzip2=True)
        res = untar(t)
        assert res == 'abc\ndef\nghi\n'

    def test_xz(self, tmpdir, monkeypatch):
        z = create_zip(tmpdir, monkeypatch)
        t = z2t(z, xz=True)
        res = untar(t)
        assert res == 'abc\ndef\nghi\n'

    def test_no_date(self, tmpdir, monkeypatch):
        monkeypatch.setenv('TZ', 'UTC')
        z = create_zip(tmpdir, monkeypatch)
        t = z2t(z, bzip2=True, no_date=True)
        res = subprocess.check_output(['tar', 'tvf', str(t)]).decode('ascii')
        assert res == dedent("""\
        -rw-r--r-- 0/0               3 1970-01-01 00:00 abc
        -rw-r--r-- 0/0               3 1970-01-01 00:00 def
        -rw-r--r-- 0/0               3 1970-01-01 00:00 ghi
        """)
