#! /usr/bin/env python
# coding: utf-8

from __future__ import print_function

import sys
import os

name_space = 'ruamel'
package_name = 'zip2tar'
full_package_name = name_space + '.' + package_name

exclude_files = [
    'setup.py',
]


def get_version():
    v_i = 'version_info = '
    for line in open('__init__.py'):
        if not line.startswith(v_i):
            continue
        s_e = line[len(v_i):].strip()[1:-1].split(', ')
        els = [x.strip()[1:-1] if x[0] in '\'"' else int(x) for x in s_e]
        return els


def _check_convert_version(tup):
    """Create a PEP 386 pseudo-format conformant string from tuple tup."""
    ret_val = str(tup[0])  # first is always digit
    next_sep = "."  # separator for next extension, can be "" or "."
    nr_digits = 0  # nr of adjacent digits in rest, to verify
    post_dev = False  # are we processig post/dev
    for x in tup[1:]:
        if isinstance(x, int):
            nr_digits += 1
            if nr_digits > 2:
                raise ValueError("too many consecutive digits " + ret_val)
            ret_val += next_sep + str(x)
            next_sep = '.'
            continue
        first_letter = x[0].lower()
        next_sep = ''
        if first_letter in 'abcr':
            if post_dev:
                raise ValueError("release level specified after "
                                 "post/dev:" + x)
            nr_digits = 0
            ret_val += 'rc' if first_letter == 'r' else first_letter
        elif first_letter in 'pd':
            nr_digits = 1  # only one can follow
            post_dev = True
            ret_val += '.post' if first_letter == 'p' else '.dev'
        else:
            raise ValueError('First letter of "' + x + '" not recognised')
    return ret_val


version_info = get_version()
version_str = _check_convert_version(version_info)

if __name__ == '__main__':
    # put here so setup.py can be imported more easily
    from setuptools import setup, find_packages
    from setuptools.command import install_lib


class MyInstallLib(install_lib.install_lib):
    def run(self):
        install_lib.install_lib.run(self)

    def install(self):
        fpp = full_package_name.split('.')  # full package path
        full_exclude_files = [os.path.join(*(fpp + [x]))
                              for x in exclude_files]
        alt_files = []
        outfiles = install_lib.install_lib.install(self)
        for x in outfiles:
            for full_exclude_file in full_exclude_files:
                if full_exclude_file in x:
                    os.remove(x)
                    break
            else:
                alt_files.append(x)
        return alt_files


def main():
    # for 2.6 support missing (at least):
    # - ZipFile as context
    # - check_output in the tests
    assert sys.version_info >= (2, 7)
    install_requires = []
    if sys.version_info < (3, ):
        install_requires.append("pyliblzma")
    packages = [full_package_name] + [(full_package_name + '.' + x) for x
                                      in find_packages(exclude=['tests'])]
    setup(
        name=full_package_name,
        version=version_str,
        description="""zip2tar, a zipfile to tar convertor without intermediate
        files""",
        install_requires=install_requires,
        long_description=open('README.rst').read(),
        url='https://bitbucket.org/ruamel/' + package_name,
        author='Anthon van der Neut',
        author_email='a.van.der.neut@ruamel.eu',
        license="MIT license",
        package_dir={full_package_name: '.'},
        namespace_packages=[name_space],
        packages=packages,
        entry_points=mk_entry_points(full_package_name),
        cmdclass={'install_lib': MyInstallLib},
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
        ]
    )


def mk_entry_points(full_package_name):
    script_name = package_name.replace('.', '_')
    # script_name = full_package_name.rsplit('.', 1)[-1] # no prefix
    return {'console_scripts': [
        '{0} = {1}:main'.format(script_name, full_package_name),
    ]}

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sdist':
        abs_path = os.path.abspath(os.path.dirname(__file__))
        if 'site-packages' in abs_path:
            assert full_package_name == abs_path.split(
                'site-packages' + os.path.sep)[1].replace(
                os.path.sep, '.')
    main()
