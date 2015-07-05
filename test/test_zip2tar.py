# coding 'utf-8'

from __future__ import print_function

import os
import subprocess

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

def z2t(zip_file, gzip=False, bzip2=False, xz=False):
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
    cmd.append(str(zip_file))
    subprocess.check_output(cmd)
    return zip_file.new(ext=ext)

def untar(tar_file):
    return subprocess.check_output(['tar', 'tf', str(tar_file)]).decode('ascii')


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

