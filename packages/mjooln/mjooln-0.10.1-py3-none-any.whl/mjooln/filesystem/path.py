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

import importlib.metadata as md

from mjooln.environment import PIXIE
from mjooln.exception import PixieInPipeline
from mjooln.primitives import Zulu

try:
    __version__: str = md.version("mjooln")
except md.PackageNotFoundError:
    __version__ = "N/A"

import logging
import os
import socket

from pathlib import Path as Path_
from pathlib import PurePath
from sys import platform


from mjooln.exception import PathError
from mjooln.core import Glass


# TODO: Add the lack of speed in documentation. Not meant to be used
# for large folders (thats the whole point)
class Path(Glass):
    """Absolute paths as an instance with convenience functions

    Intended use via subclasses :class:`.Folder` and :class:`.File`

    No relative paths are allowed. Paths not starting with a valid
    mountpoint will be based in current folder

    All backslashes are replaced with :data:`FOLDER_SEPARATOR`
    """

    logger = logging.getLogger(__name__)

    FOLDER_SEPARATOR = "/"
    PATH_CHARACTER_LIMIT = 256

    LINUX = "linux"
    WINDOWS = "windows"
    OSX = "osx"
    PLATFORM = {"linux": LINUX, "linux2": LINUX, "darwin": OSX, "win32": WINDOWS}

    try:
        # Import psutil if it exists. This makes it possible
        # to use this module on Windows without installing psutil,
        # which again requires Visual Studio C++ Build Tools
        from psutil import disk_partitions  # type: ignore

        __disk_partitions = disk_partitions
    except ModuleNotFoundError:
        __disk_partitions = None

    @classmethod
    def platform(cls):
        """
        Get platform name alias

            - :data:`WINDOWS`
            - :data:`LINUX`
            - :data:`OSX`

        Example on a linux platform::

            Path.platform()
                'linux'

            Path.platform() == Path.LINUX
                True

        :raises PathError: If platform is unknown
        :return: Platform name alias
        :rtype: str
        """
        if platform in cls.PLATFORM:
            return cls.PLATFORM[platform]
        else:
            raise PathError(
                f"Unknown platform {platform}. "
                f"Known platforms are: {cls.PLATFORM.keys()}"
            )

    @classmethod
    def host(cls):
        """Get host name

        Wrapper for ``socket.gethostname()``

        :return: Host name
        :rtype: str
        """
        return socket.gethostname()

    @classmethod
    def _join(cls, *args):
        return os.path.join(*args)

    @classmethod
    def join(cls, *args):
        """Join strings to path

        Wrapper for ``os.path.join()``

        Relative paths will include current folder::

            Path.current()
                '/Users/zaphod/dev'
            Path.join('code', 'donald')
                '/Users/zaphod/dev/code/donald'

        :return: Joined path as absolute path
        :rtype: Path
        """
        return cls(cls._join(*args))

    @classmethod
    def mountpoints(cls):
        # TODO: Add limit on levels or something to only get relevant partitions
        """List valid mountpoints/partitions or drives

        Finds mountpoints/partitions on linux/osx, and drives (C:, D:) on
        windows.

        .. warning:: Windows requires installing package with an extra:
            ``mjooln[mp]``.
            Alternatively, install package ``psutil`` manually

        .. warning:: Network drives on windows will not be found by this method,
            unless they have been mapped

        .. note:: Requires installation of Visual Studio C++ Build Tools on Windows.
            Go to the download page
            and find the Build Tools download (this is why the package
            ``psutil`` is not included by default on Windows)

        :return: Valid mountpoints or drives
        :rtype: list
        """
        if cls.__disk_partitions is None:
            raise PathError(
                "Method requires module 'psutil' "
                "installed. The module is not included in "
                "requirements since it requires "
                "Visual Studio C++ Build Tools on Windows. If "
                "you are not using Windows, simply install "
                "this package as mjooln[mountpoints]"
                "package handler. If you are on Windows, go "
                "to https://visualstudio.microsoft.com/downloads/ "
                "and find the Build Tools download"
            )
        from mjooln import Folder

        mps = [
            Folder(x.mountpoint.replace("\\", cls.FOLDER_SEPARATOR))
            for x in cls.__disk_partitions(all=True)
            if os.path.isdir(x.mountpoint)
        ]
        # Remove duplicates (got double instance of root in a terraform vm)
        return list(set(mps))

    @classmethod
    def has_valid_mountpoint(cls, path_str):
        """Flags if the path starts with a valid mountpoint

        Wrapper for ``os.path.isabs()``

        :return: True if path has valid mountpoint, False if not
        :rtype: bool
        """
        if cls.platform() == cls.WINDOWS and cls.is_network_drive(path_str):
            return True
        return os.path.isabs(path_str)

    @classmethod
    def listdir(cls, path_str):
        """
        List folder content as plain strings with relative path names

        Wrapper for ``os.listdir()``

        Other list and walk methods in :class:`Folder` will instantiate
        :class:`File` or :class:`Folder` objects. They are thus a bit slower

        :param path_str: String with path to folder
        :return: List of relative path strings
        """
        return os.listdir(path_str)

    @classmethod
    def validate(cls, path_str):
        """
        Check if path is longer than :data:`PATH_CHARACTER_LIMIT`, which
        on Windows may cause problems

        :param path_str: Path to check
        :type path_str: str
        :raises PathError: If path is too long
        """
        if len(path_str) > cls.PATH_CHARACTER_LIMIT:
            raise PathError(
                f"Path exceeds {cls.PATH_CHARACTER_LIMIT} "
                f"characters, which may cause problems on "
                f"some platforms"
            )
        # TODO: Add check on characters in path

    def __init__(self, path: str):
        if PIXIE and not isinstance(path, str):
            raise PixieInPipeline("Input to Path constructor must be of type str")
        if path.startswith("~"):
            path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = path.replace("\\", self.FOLDER_SEPARATOR)
            path = os.path.abspath(path)
        path = path.replace("\\", self.FOLDER_SEPARATOR)
        if PIXIE:
            try:
                self.validate(path)
            except PathError as pe:
                raise PixieInPipeline(f"Invalid path: {path}") from pe
        self.__path = path

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return self.__path

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    # Make pandas (and other libraries) recognize Path class as pathlike
    def __fspath__(self):
        return str(self)

    def __repr__(self):
        return f"Path('{self.__path}')"

    def _rename(self, new_path: str):
        self.__path = new_path

    def as_file(self):
        """
        Create :class:`File` with same path

        :rtype: File
        """
        from mjooln import File

        return File(self.__path)

    def as_folder(self):
        """
        Create :class:`Folder` with same path

        :rtype: Folder
        """
        from mjooln import Folder

        return Folder(self.__path)

    def as_path(self):
        """
        Get as ``pathlib.Path`` object

        :return: path
        :rtype: pathlib.Path
        """
        return Path_(str(self))

    def as_pure_path(self):
        """
        Get as ``pathlib.PurePath`` object

        :return: path
        :rtype: pathlib.PurePath
        """
        return PurePath(str(self))

    def name(self):
        """Get name of folder or file

        Example::

            p = Path('/Users/zaphod')
            p
                '/Users/zaphod
            p.name()
                'zaphod'

            p2 = Path(p, 'dev', 'code', 'donald')
            p2
                '/Users/zaphod/dev/code/donald'
            p2.name()
                'donald'

            p3 = Path(p, 'dev', 'code', 'donald', 'content.txt')
            p3
                '/Users/zaphod/dev/code/donald/content.txt'
            p3.name()
                'content.txt'

        :return: Folder or file name
        :rtype: str
        """
        return os.path.basename(str(self))

    def volume(self):
        """Return path volume

        Volume is a collective term for mountpoint, drive and network drive

        :raises PathError: If volume cannot be determined
        :return: Volume of path
        :rtype: Folder
        """
        from mjooln import Folder

        try:
            return self.network_drive()
        except PathError:
            pass
        path = os.path.abspath(str(self))
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return Folder(path)

    def exists(self):
        """Check if path exists

        Wrapper for ``os.path.exists()``

        :return: True if path exists, False otherwise
        :rtype: bool
        """
        return os.path.exists(self)

    def raise_if_not_exists(self):
        """Raises an exception if path does not exist

        :raises PathError: If path does not exist
        """
        if not self.exists():
            raise PathError(f"Path does not exist: {self}")

    def is_volume(self):
        """
        Check if path is a volume

        Volume is a collective term for mountpoint, drive and network drive

        :raises PathError: If path does not exist
        :return: True if path is a volume, False if not
        :rtype: bool
        """
        if self.exists():
            return self.is_network_drive() or self == self.volume()
        else:
            raise PathError(
                f"Cannot see if non existent path is a volume or not: {self}"
            )

    def on_network_drive(self):
        """
        Check if path is on a network drive

        .. warning:: Only checks if the path starts with double slash, and may
            be somewhat unreliable. Make sure to test if it seems to work

        :return: True if path is on network drive, False if not
        :rtype: bool
        """
        return str(self).startswith("//")

    def network_drive(self):
        """
        Returns the first part of the path following the double slash

        Example::

            p = Path('//netwdrive/extensions/parts')
            p.network_drive()
                Folder('//netwdrive')

        :raises PathError: If path is not on a network drive
            (see :meth:`on_network_drive()`)
        :return: Network drive part of the path
        :rtype: Folder
        """
        from mjooln import Folder

        if self.on_network_drive():
            return Folder("//" + self.parts()[0])
        else:
            raise PathError(f"Path is not on a network drive: {self}")

    def is_network_drive(self):
        """
        Check if path is a network drive following the same rules as
        in :meth:`on_network_drive()`

        .. note:: If on Windows, a mapped network drive will not be
            interpreted as a network drive, since the path starts with a
            drive letter

        :return: True if path is network drive, False if not
        :rtype: bool
        """
        try:
            return self.network_drive() == self
        except PathError:
            return False

    def is_folder(self):
        """
        Check if path is a folder

        :raises PathError: If path does not exist
        :return: True if path is a folder, False if not
        :rtype: bool
        """
        if self.exists():
            return os.path.isdir(self)
        else:
            raise PathError(
                f"Cannot determine if non existent path is a folder or not: {self}"
            )

    def is_file(self):
        """Check if path is a file

        :raises PathError: If path does not exist
        :return: True if path is a file, False if not
        :rtype: bool
        """
        if self.exists():
            return os.path.isfile(self)
        else:
            raise PathError(
                f"Cannot determine if non existent path is a file or not: {self}"
            )

    def size(self):
        """Return file or folder size

        .. note:: If Path is a folder, ``size()`` will return a small number,
            representing the size of the folder object, not its contents.
            For finding actual disk usage of a folder, use
            :meth:`.Folder.disk_usage()`

        :raises PathError: If path does not exist
        :returns: File or folder size
        :rtype: int
        """
        if self.exists():
            return os.stat(self).st_size
        else:
            raise PathError(f"Cannot determine size of non existent path: {self}")

    def created(self):
        """
        Get created timestamp from operating system

        Wrapper for ``os.stat(<path>).st_ctime``

        .. note:: Created timestamp tends to be unreliable, especially
            when files have been moved around

        :return: Timestamp created (perhaps)
        :rtype: Zulu
        """
        return Zulu.from_epoch(os.stat(self).st_ctime)

    def modified(self):
        """
        Get modified timestamp from operating system

        Wrapper for ``os.stat(<path>).st_mtime``

        .. note:: Modified timestamp tends to be unreliable, especially
            when files have been moved around

        :returns: Timestamp modified (perhaps)
        :rtype: Zulu
        """
        return Zulu.from_epoch(os.stat(self).st_mtime)

    def parts(self):
        """
        Get list of parts in path

        Example::

            p = Path('/home/zaphod/dev/code')
            p.parts()
                ['home', 'zaphod', 'dev', 'code']

        :returns: String parts of path
        :rtype: list
        """
        parts = str(self).split(self.FOLDER_SEPARATOR)
        # Remove empty first part (if path starts with /)
        if parts[0] == "":
            parts = parts[1:]
        # Once more in case this is a network drive
        if parts[0] == "":
            parts = parts[1:]
        return parts
