# coding 'utf-8'

from __future__ import print_function

import subprocess
import sys
from textwrap import dedent

import pytest


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


def untar(tar_file):
    cmd = ['tar', 'tf', str(tar_file)]
    return subprocess.check_output(cmd).decode('ascii')


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

    @pytest.mark.skipif(sys.version_info < (3, 4),
                        reason='requires python 3.4')
    def test_xz(self, tmpdir, monkeypatch):
        z = create_zip(tmpdir, monkeypatch)
        t = z2t(z, xz=True)
        res = untar(t)
        assert res == 'abc\ndef\nghi\n'

    def test_no_date(self, tmpdir, monkeypatch):
        z = create_zip(tmpdir, monkeypatch)
        t = z2t(z, bzip2=True, no_date=True)
        res = subprocess.check_output(['tar', 'tvf', str(t)]).decode('ascii')
        assert res == dedent("""\
        -rw-r--r-- 0/0               3 1970-01-01 01:00 abc
        -rw-r--r-- 0/0               3 1970-01-01 01:00 def
        -rw-r--r-- 0/0               3 1970-01-01 01:00 ghi
        """)
