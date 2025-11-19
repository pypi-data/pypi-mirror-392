# Copyright (c) 2020 Vemund Halmø Aarstrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gzip
import shutil
import zipfile

from .file import File
from mjooln.exception import ArchiveError


class Archive:
    """
    Zip file to gz conversion

    """

    # TODO: Add gz to zip
    # TODO: Add handling of multiple files and folders in archive

    @classmethod
    def is_zip(cls, file: File):
        """
        Check if input file is zip archive

        :param file: Input file
        :return: True if extension is 'zip', false if not
        :rtype: bool
        """
        extensions = file.extensions()
        return len(extensions) > 0 and extensions[-1] == "zip"

    @classmethod
    def zip_to_gz(cls, file: File, delete_source_file: bool = True):
        """
        Convert zip file to gzip compressed file

        :param file: Input zip archive
        :param delete_source_file: Delete source file if True
        """

        if not cls.is_zip(file):
            raise ArchiveError(f"File is not zip-file: {file}")

        with zipfile.ZipFile(file, "r") as zr:
            file_info_li = zr.filelist
            if len(file_info_li) > 1:
                raise ArchiveError(f"Multiple files in archive: {file}")
            elif len(file_info_li) == 0:
                raise ArchiveError(f"No files in archive: {file}")
            file_info = file_info_li[0]
            file_name = file_info.filename
            if "/" in file_name:
                file_name = file_name.split("/")[-1]
            if "\\" in file_name:
                file_name = file_name.split("\\")[-1]
            gz_file = File.join(file.folder(), file_name + ".gz")
            with zr.open(file_info, "r") as zf:
                with gzip.open(gz_file, "w") as gf:
                    shutil.copyfileobj(zf, gf)

        if delete_source_file:
            file.delete()

        return gz_file
