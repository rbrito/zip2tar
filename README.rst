
``zip2tar`` is an in memory zip to tar convertor.

No intermediate files are created on disc.
By default non-compressed tar is created, but can specify
commandline options to get gzip, bzip2 or xz compressed
tar archives.

The output filename can be set explicitly with ``--tar-file-name``, but is
normally derived by replacing "``.zip``" with "``.tar``", "``.tar.xz``",
"``.tar.bz2``" or "``.tar.gz``".

The ``--md5`` option adds a file ``md5.sum`` to the tar file (a file with
that name cannot already be in the zip file). After extracting, you can do
``md5sum -c md5.sum`` to check the files for corruption. These md5 sums are
calculated from the in-memory extracted data and are **not** based on the
zip's CRC information.

On Python 2.7 this requires 'pyliblzma'

::

  usage: zip2tar [-h] [--verbose] [--xz] [--bz2] [--gz]
                 [--compression-level COMPRESSION_LEVEL] [--no-datetime]
                 [--tar-file-name NAME] [--md5] [--version]
                 filename

  in-memory zip to tar convertor

  positional arguments:
    filename

  optional arguments:
    -h, --help            show this help message and exit
    --verbose, -v         increase verbosity level
    --xz                  write xz compressed tar file
    --bz2                 write bzip2 compressed tar file
    --gz                  write gzip compressed tar file
    --compression-level COMPRESSION_LEVEL
    --no-datetime         don't take datetime for files from zip -> 1970-01-01
    --tar-file-name NAME  set tar file name (normally derived from .zip)
    --md5                 add a 'sum.md5' file (cannot already be in the zip)
    --version             show program's version number and exit
