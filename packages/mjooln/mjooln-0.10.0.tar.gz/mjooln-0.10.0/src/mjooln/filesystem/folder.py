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

import glob
import os
import shutil

from .path import Path
from mjooln.environment import PIXIE
from mjooln.exception import PixieInPipeline, FolderError, PathError, FileError
from mjooln.utils import Math
from mjooln.primitives import Key


class Folder(Path):
    @classmethod
    def home(cls):
        """Get path to user home folder

        Wrapper for ``os.path.expanduser()``

        :return: Home folder path
        :rtype: Folder
        """
        return Folder(os.path.expanduser("~"))

    @classmethod
    def current(cls):
        """Get current folder path

        Wrapper for ``os.getcwd()``

        :return: Path to current folder
        :rtype: Folder
        """
        return cls(os.getcwd())

    def __init__(self, path, *args, **kwargs):
        super().__init__(path)
        if PIXIE:
            if self.exists():
                if self.is_file():
                    raise PixieInPipeline(f"Path is a file, not a folder: {self}")

    def __repr__(self):
        return f"Folder('{self}')"

    def __truediv__(self, other):
        from mjooln import Word

        if isinstance(other, str) or isinstance(other, Word) or isinstance(other, Key):
            return self.append(other)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, str):
            return self.file(other)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Folder):
            str_self = str(self)
            str_other = str(other)
            if str_self.startswith(str_other):
                new_str = str_self[len(str(other)) :]
                if new_str.startswith("/"):
                    new_str = new_str[1:]
                return new_str
            else:
                raise FolderError(
                    f"Cannot subtract folder which is not part of other; "
                    f"This: {str_self};"
                    f"Other: {str_other}; "
                    f"This must start with Other"
                )
        return NotImplemented

    def create(self, error_if_exists=True):
        """Create new folder, including non existent parent folders

        :raises FolderError: If folder already exists,
            *and* ``error_if_exists=True``
        :param error_if_exists: Error flag. If True, method will raise an
            error if the folder already exists
        :type error_if_exists: bool
        :returns: True if it was created, False if not
        :rtype: bool
        """
        if not self.exists():
            os.makedirs(self)
            return True
        else:
            if error_if_exists:
                raise FolderError(f"Folder already exists: {self}")
            return False

    def touch(self):
        """
        Create folder if it does not exist, ignore otherwise
        """
        self.create(error_if_exists=False)

    def untouch(self):
        """
        Remove folder if it exists, ignore otherwise

        :raises OSError: If folder exists but is not empty
        """
        self.remove(error_if_not_exists=False)

    def parent(self):
        """Get parent folder

        :return: Parent folder
        :rtype: Folder
        """
        return Folder(os.path.dirname(str(self)))

    def append(self, *args):
        """Append strings or list of strings to current folder

        Example::

            fo = Folder.home()
            print(fo)
                '/Users/zaphod'

            fo.append('dev', 'code', 'donald')
                '/Users/zaphod/dev/code/donald'

            parts = ['dev', 'code', 'donald']
            fo.append(parts)
                '/Users/zaphod/dev/code/donald'

        :param args: Strings or list of strings
        :return: Appended folder as separate object
        :rtype: Folder
        """
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, list):
                arg = [str(x) for x in arg]
                return Folder.join(str(self), "/".join(arg))
            elif isinstance(arg, Key):
                return Folder.join(str(self), "/".join([str(x) for x in arg.words()]))
            else:
                return Folder.join(str(self), str(arg))
        else:
            return Folder.join(str(self), *args)

    def file(self, name: str):
        """
        Create file path in this folder

        :param name: File name
        :type name: str
        :return: File path in this folder
        :rtype: File
        """
        from mjooln import File

        if PIXIE:
            if os.path.abspath(name) == name:
                raise PixieInPipeline(f"File name is already full path: {name}")
        return File.join(str(self), name)

    def is_empty(self):
        """Check if folder is empty

        :raise FolderError: If folder does not exist
        :return: True if empty, False if not
        :rtype: bool
        """
        if self.exists():
            return len(list(self.list())) == 0
        else:
            raise FolderError(f"Cannot check if non existent folder is empty: {self}")

    # TODO: Add test for empty, with missing name
    def empty(self, name: str):
        """
        Recursively deletes all files and subfolders

        Name of folder is required to verify deleting content

        .. warning:: Be careful. Will delete  all content recursively

        :param name: Folder name as given by :meth:`.Folder.name()`.
            Required to verify deleting all contents
        :type name: str
        :raises FolderError: If folder does not exist, or if ``name`` is not
            an exact match with folder name
        """
        if self.name() != name:
            raise FolderError(
                f"Text of folder required to verify deletion: name={self.name()}"
            )
        if self.exists():
            for name in os.listdir(self):
                path = os.path.join(self, name)
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        else:
            raise FolderError(f"Cannot empty a non existent folder: {self}")

    def remove(self, error_if_not_exists: bool = True):
        """
        Remove folder

        :raises OSError: If folder exists but is not empty
        :raises FolderError: If folder does not exist and
            ``error_if_not_exists=True``
        :param error_if_not_exists: If True, method will raise an
            error if the folder already exists
        :type error_if_not_exists: bool
        """
        if self.exists():
            os.rmdir(str(self))
        else:
            if error_if_not_exists:
                raise FolderError(f"Cannot remove a non existent folder: {self}")

    def remove_empty_folders(self):
        """
        Recursively remove empty subfolders
        """
        fo_str = str(self)
        for root, folders, files in os.walk(fo_str):
            if root != fo_str and not folders and not files:
                os.rmdir(root)

    def list(self, pattern: str = "*", recursive: bool = False):
        """
        List folder contents

        Example patterns:

            - ``'*'`` (default) Returns all files and folders except hidden
            - ``'.*`` Returns all hidden files and folders
            - ``'*.txt'`` Return all files ending with 'txt'

        .. note:: For large amounts of files and folders, use the generator
            returned by :meth:`.Folder.walk()` and handle them individually

        :raises FolderError: If folder does not exist
        :param pattern: Pattern to search for
        :param recursive: If True search will include all subfolders and files
        :return: List of :class:`.File` and/or :class:`Folder`
        :rtype: list
        """
        from mjooln import File

        if not self.exists():
            raise FolderError(f"Cannot list non existent folder: {self}")

        if recursive:
            paths = glob.glob(str(self.append("**", pattern)), recursive=True)
        elif pattern is None:
            paths = os.listdir(str(self))
        else:
            paths = glob.glob(str(self.append(pattern)))

        fifo_paths: list[File | Folder] = []
        for path in paths:
            try:
                if os.path.isfile(path):
                    fifo_paths.append(File(path))
                elif os.path.isdir(path):
                    fifo_paths.append(Folder(path))
            except FileError or PathError or FolderError as e:  # type: ignore
                # TODO: Handle links and other exceptions
                self.logger.info(f"Skipping path {path} due to error: {e}")
        return fifo_paths

    def list_files(self, pattern="*", recursive=False):
        """
        List all files in this folder matching ``pattern``

        Uses :meth:`.Folder.list()` and then filters out all :class:`.File`
        objects and returns the result

        .. note:: For large amounts of files, use the generator
            returned by :meth:`.Folder.files()` and handle them individually

        :raises FolderError: If folder does not exist
        :param pattern: Pattern to search for
        :param recursive: If True search will include all subfolders and files
        :return: List of :class:`.File` objects
        :rtype: list
        """
        from mjooln import File

        paths = self.list(pattern=pattern, recursive=recursive)
        return [x for x in paths if isinstance(x, File)]

    def list_folders(self, pattern="*", recursive=False):
        """
        List all folders in this folder matching ``pattern``

        Uses :meth:`.Folder.list()` and then filters out all :class:`.Folder`
        objects and returns the result

        .. note:: For large amounts of folders, use the generator
            returned by :meth:`.Folder.folders()` and handle them individually

        :raises FolderError: If folder does not exist
        :param pattern: Pattern to search for
        :param recursive: If True search will include all subfolders and files
        :return: List of :class:`.Folder` objects
        :rtype: list
        """
        paths = self.list(pattern=pattern, recursive=recursive)
        return [x for x in paths if isinstance(x, Folder)]

    def walk(self, include_files: bool = True, include_folders: bool = True):
        """
        Generator listing all files and folders in this folder recursively

        :return: Generator object returning :class:`File` or :class:`Folder`
            for each iteration
        :rtype: generator
        """
        from mjooln import File

        for root, fos, fis in os.walk(str(self)):
            if include_folders:
                for fo in (Folder.join(root, x) for x in fos):
                    if fo.exists():
                        yield fo
            if include_files:
                for fi in (File.join(root, x) for x in fis):
                    if fi.exists():
                        yield fi

    def files(self):
        """
        Generator listing all files in this folder recursively

        Print all files larger than 1 kB in home folder and all subfolders::

            fo = Folder.home()
            for fi in fo.files():
                if fi.size() > 1000:
                    print(fi)

        :return: Generator object returning :class:`File` for each iteration
        :rtype: generator
        """
        return self.walk(include_files=True, include_folders=False)

    def folders(self):
        """
        Generator listing all folders in this folder recursively

        :return: Generator object returning :class:`Folder` for each iteration
        :rtype: generator
        """
        return self.walk(include_files=False, include_folders=True)

    def count(self, include_files: bool = True, include_folders: bool = True):
        """
        Count number of files and/or folders recursively

        .. note:: Links will also be included

        :param include_files: Include files in count
        :type include_files: bool
        :param include_folders: Include folders in count
        :type include_folders: bool
        :return: Number of files and/or folders in folder
        :rtype: int
        """
        count = 0
        for root, fos, fis in os.walk(str(self)):
            if include_folders:
                count += len(fos)
            if include_files:
                count += len(fis)
        return count

    def count_files(self):
        """
        Count number of files recursively

        .. note:: Links will also be included

        :return: Number of files in folder
        :rtype: int
        """
        return self.count(include_files=True, include_folders=False)

    def count_folders(self):
        """
        Count number of folders recursively

        .. note:: Links will also be included

        :return: Number of folders in folder
        :rtype: int
        """
        return self.count(include_files=False, include_folders=True)

    def disk_usage(self, include_folders: bool = False, include_files: bool = True):
        """
        Recursively determines disk usage of all contents in folder

        :param include_folders: If True, all folder sizes will be included in
            total, but this is only the folder object and hence a small number.
            Default is therefore False
        :param include_files: If True, all file sizes are included in total.
            Default is obviously True
        :raises FolderError: If folder does not exist
        :return: Disk usage of folder content
        :rtype: int
        """
        if not self.exists():
            raise FolderError(
                f"Cannot determine disk usage of non existent folder: {self}"
            )
        size = 0
        for root, fos, fis in os.walk(str(self)):
            if include_folders:
                for fo in fos:
                    try:
                        size += os.stat(os.path.join(root, fo)).st_size
                    except FileNotFoundError:
                        pass
            if include_files:
                for fi in fis:
                    try:
                        size += os.stat(os.path.join(root, fi)).st_size
                    except FileNotFoundError:
                        pass
        return size

    def print(self, count: bool = False, disk_usage: bool = False):
        """
        Print folder content

        :param count: Include count for each subfolder
        :type count: bool
        :param disk_usage: Include disk usage for each subfolder, and size
            for each file
        :type disk_usage: bool
        """
        paths = self.list()
        for path in paths:
            if not path.exists():
                print(f"{path.name()} [link or deleted]")
            else:
                if path.is_folder():
                    print(f"{path.name()} [Folder]")
                    if count or disk_usage:
                        fo = Folder(str(path))
                        if count:
                            nfo = fo.count_folders()
                            print(f"\tSubfolder count: {nfo}")
                            nfi = fo.count_files()
                            print(f"\tFile count: {nfi}")
                        if disk_usage:
                            du = fo.disk_usage()
                            dustr = Math.bytes_to_human(du)
                            print(f"\tDisk usage: {dustr}")
                elif path.is_file():
                    from mjooln import File

                    print(f"{path.name()} [File]")
                    if disk_usage:
                        fi = File(str(path))
                        size = Math.bytes_to_human(fi.size())
                        print(f"\tSize: {size}")
                else:
                    print(f"{path.name()} [unknown]")
