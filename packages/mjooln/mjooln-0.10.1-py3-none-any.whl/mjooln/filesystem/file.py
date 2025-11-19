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
import hashlib
import logging
import os
import shutil

from pathlib import Path as Path_

from mjooln.environment import COMPRESSED_EXTENSION, ENCRYPTED_EXTENSION, PIXIE
from mjooln.exception import FileError, PixieInPipeline
from mjooln.encryption import Crypt

from .serializer import Serializer
from .path import Path
from .folder import Folder


class File(Path):
    """
    Convenience class for file handling

    Create a file path in current folder::

        fi = File('my_file.txt')
        fi
            File('/home/zaphod/current/my_file.txt')

    Create a file path in home folder::

        fi = File.home('my_file.txt')
        fi
            File('/home/zaphod/my_file.txt')

    Create a file path in some folder::

        fo = Folder.home().append('some/folder')
        fo
            Folder('/home/zaphod/some/folder')
        fi = fo.file('my_file.txt')
        fi
            File('/home/zaphod/some/folder/my_file.txt')

    Create and read a file::

        fi = File('my_file.txt')
        fi.write('Hello world')
        fi.read()
            'Hello world'
        fi.size()
            11

    Compress and encrypt::

        fi.compress()
        fi.name()
            'my_file.txt.gz'
        fi.read()
            'Hello world'

        crypt_key = Crypt.generate_key()
        crypt_key
            b'aLQYOIxZOLllYThEKoXTH_eqTQGEnXm9CUl2glq3a2M='
        fi.encrypt(crypt_key)
        fi.name()
            'my_file.txt.gz.aes'
        fi.read(crypt_key=crypt_key)
            'Hello world'

    Create an encrypted file, and write to it::

        ff = File('my_special_file.txt.aes')
        ff.write('Hello there', password='123')
        ff.read(password='123')
            'Hello there'

        f = open(ff)
        f.read()
            'gAAAAABe0BYqPPYfzha3AKNyQCorg4TT8DcJ4XxtYhMs7ksx22GiVC03WcrMTnvJLjTLNYCz_N6OCmSVwk29Q9hoQ-UkN0Sbbg=='
        f.close()

    .. note:: Using the ``password`` parameter, builds an encryption key by
        combining it with the builtin (i.e. hard coded) class salt.
        For proper security, generate your
        own salt with :meth:`.Crypt.salt()`. Store this salt appropriately,
        then use :meth:`.Crypt.key_from_password()` to generate a crypt_key

    .. warning:: \'123\' is not a real password

    """

    _salt = b"O89ogfFYLGUts3BM1dat4vcQ"

    logger = logging.getLogger(__name__)

    #: Files with this extension will compress text before writing to file
    #: and decompress after reading
    COMPRESSED_EXTENSION = COMPRESSED_EXTENSION

    #: Files with this extension will encrypt before writing to file, and
    #: decrypt after reading. The read/write methods therefore require a
    #: crypt_key
    ENCRYPTED_EXTENSION = ENCRYPTED_EXTENSION

    JSON_EXTENSION = "json"
    YAML_EXTENSION = "yaml"

    # #: Extensions reserved for compression and encryption
    # RESERVED_EXTENSIONS = [COMPRESSED_EXTENSION,
    #                        ENCRYPTED_EXTENSION]

    #: File names starting with this character will be tagged as hidden
    HIDDEN_STARTSWITH = "."

    #: Extension separator. Period
    EXTENSION_SEPARATOR = "."

    # TODO: Add binary flag based on extension (all other than text is binary..)
    # TODO: Facilitate child classes with custom read/write needs

    @classmethod
    def make(
        cls,
        folder,
        stub: str,
        extension: str,
        is_hidden: bool = False,
        is_compressed: bool = False,
        is_encrypted: bool = False,
    ):
        """
        Create a file path following proper file name structure

        :param folder: Containing folder
        :type folder: Folder
        :param stub: File stub
        :type stub: str
        :param extension: File extension added after file stub
        :type extension: str
        :param is_hidden: Whether file is hidden or not. True will add
             :data:`HIDDEN_STARTSWITH` to beginning of filename
        :type is_hidden: bool
        :param is_compressed: True will add the :data:`COMPRESSED_EXTENSION`
            after the regular extension
        :type is_compressed: bool
        :param is_encrypted: True will add the :data:`ENCRYPTED_EXTENSION`
            after the regular extension and possible compressed extension
        :type is_encrypted: bool
        :rtype: File
        """
        folder = Folder.glass(folder)
        names = [stub, extension]
        if is_compressed:
            names += [cls.COMPRESSED_EXTENSION]
        if is_encrypted:
            names += [cls.ENCRYPTED_EXTENSION]
        name = cls.EXTENSION_SEPARATOR.join(names)
        if is_hidden:
            name = cls.HIDDEN_STARTSWITH + name

        return cls.join(folder, name)

    @classmethod
    def home(cls, file_name: str):
        """
        Create a file path in home folder

        :param file_name: File name
        :type file_name: str
        :rtype: File
        """
        from mjooln import Folder

        return cls.join(Folder.home(), file_name)

    @classmethod
    def _crypt_key(cls, crypt_key: bytes | None = None, password: str | None = None):
        if crypt_key is None and password is None:
            raise FileError("crypt_key or password missing")
        elif crypt_key is not None and password is not None:
            raise FileError("Use either crypt_key or password.")
        if crypt_key is not None:
            return crypt_key
        elif password is not None:
            return Crypt.key_from_password(cls._salt, password)
        else:
            raise FileError("FATAL: This should be unreachable")

    def __init__(self, path: str, *args, **kwargs):
        super().__init__(path)
        if PIXIE:
            if self.exists():
                if self.is_volume():
                    raise PixieInPipeline(f"Path is volume, not file: {path}")
                elif self.is_folder():
                    raise PixieInPipeline(f"Path is existing folder, not file: {path}")
        # Lazy parsing of file name to avoid unnecessary processing
        self.__name_is_parsed = False
        self.__parts = None
        self.__stub: str | None = None
        self.__extension: str | None = None
        self.__extensions: list[str] = []
        self.__hidden: bool | None = None
        self.__compressed: bool | None = None
        self.__encrypted: bool | None = None

    def __repr__(self):
        return f"File('{self}')"

    def _rename(self, new_path: str):
        super()._rename(new_path)
        self.__name_is_parsed = False

    def _parse_name(self):
        if not self.__name_is_parsed:
            name = self.name()
            self.__hidden = name.startswith(self.HIDDEN_STARTSWITH)
            if self.__hidden:
                name = name[1:]
            parts = name.split(self.EXTENSION_SEPARATOR)
            while not parts[0]:
                parts = parts[1:]
            self.__parts = parts.copy()
            self.__stub = parts[0]
            parts = parts[1:]
            self.__extension = None
            self.__extensions = parts
            self.__compressed = False
            self.__encrypted = False
            if parts and parts[-1] == self.ENCRYPTED_EXTENSION:
                self.__encrypted = True
                parts = parts[:-1]

            if parts and parts[-1] == self.COMPRESSED_EXTENSION:
                self.__compressed = True
                parts = parts[:-1]

            if len(parts) == 1:
                self.__extension = self.__extensions[0]
            self.__name_is_parsed = True

    def parts(self):
        """
        Get file parts, i.e. those separated by period

        :return: list
        """
        self._parse_name()
        return self.__parts

    def touch(self):
        """
        Create empty file if it does not exist already
        """
        self.folder().touch()
        Path_(self).touch()

    def untouch(self, ignore_if_not_empty=False):
        """
        Delete file if it exists, and is empty

        :param ignore_if_not_empty: If True, no exception is raised if file
            is not empty and thus cannot be deleted with untouch
        :return:
        """
        if self.exists():
            if self.size() == 0:
                self.delete()
            else:
                if not ignore_if_not_empty:
                    raise FileError(
                        f"Cannot untouch file "
                        f"that is not empty: {self}; "
                        f"Use delete() to delete a non-empty file"
                    )

    def extensions(self):
        """
        Get file extensions as a list of strings

        :return: List of file extensions
        :rtype: list
        """
        self._parse_name()
        return self.__extensions

    def is_hidden(self):
        """
        Check if file is hidden, i.e. starts with :data:`HIDDEN_STARTSWITH`

        :return: True if hidden, False if not
        :rtype: bool
        """
        self._parse_name()
        return self.__hidden

    def is_compressed(self):
        """
        Check if file is compressed, i.e. has :data:`COMPRESSED_EXTENSION`

        :return: True if compressed, False if not
        :rtype: bool
        """
        self._parse_name()
        return self.__compressed

    def is_encrypted(self):
        """
        Check if file is encrypted, i.e. has :data:`ENCRYPTED_EXTENSION`

        :return: True if encrypted, False if not
        :rtype: bool
        """
        self._parse_name()
        return self.__encrypted

    def stub(self):
        """
        Get file stub, i.e. the part of the file name bar extensions and
        :data:`HIDDEN_STARTSWITH`

        Example::

            fi = File('.hidden_with_extensions.json.gz')
            fi.stub()
                'hidden_with_extensions'

        :return: File stub
        :rtype: str
        """
        self._parse_name()
        return self.__stub

    def extension(self):
        """
        Get file extension, i.e. the extension which is not reserved.
        A file is only supposed to have one extension that does not indicate
        either compression or encryption.

        :raise FileError: If file has more than one extension barring
            :data:`COMPRESSED_EXTENSION` and :data:`ENCRYPTED_EXTENSION`
        :return: File extension
        :rtype: str
        """
        self._parse_name()
        return self.__extension

    def md5_checksum(self, usedforsecurity=False):
        """
        Get MD5 Checksum for the file

        :raise FileError: If file does not exist
        :return: MD5 Checksum
        :rtype: str
        """
        if not self.exists():
            raise FileError(f"Cannot make checksum if file does not exist: {self}")
        md5 = hashlib.md5(usedforsecurity=usedforsecurity)
        with open(self, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def new(self, name):
        """
        Create a new file path in same folder as current file

        :param name: New file name
        :rtype: File
        """
        return self.folder().file(name)

    def delete(self, missing_ok: bool = False):
        """
        Delete file

        :raise FileError: If file is missing, and ``missing_ok=False``
        :param missing_ok: Indicate if an exception should be raised if the
            file is missing. If True, an exception will not be raised
        :type missing_ok: bool
        """
        if self.exists():
            self.logger.debug(f"Delete file: {self}")
            os.unlink(self)
        elif not missing_ok:
            raise FileError(f"Tried to delete file that doesn't exist: {self}")

    def delete_if_exists(self):
        """
        Delete file if exists
        """
        self.delete(missing_ok=True)

    def write(
        self,
        data,
        mode="w",
        crypt_key: bytes | None = None,
        password: str | None = None,
        **kwargs,
    ):
        """
        Write data to file

        For encryption, use either ``crypt_key`` or ``password``. None or both
        will raise an exception. Encryption requires the file name to end with
        :data:`ENCRYPTED_EXTENSION`

        :raise FileError: If using ``crypt_key`` or ``password``, and the
            file does not have encrypted extension
        :param data: Data to write
        :type data: str or bytes
        :param mode: Write mode
        :type mode: str
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        """
        if PIXIE and (crypt_key or password) and not self.is_encrypted():
            raise PixieInPipeline(
                f"File does not have crypt extension "
                f"({self.ENCRYPTED_EXTENSION}), "
                f"but a crypt_key "
                f"or password was sent as input to write."
            )

        if self.is_encrypted():
            crypt_key = self._crypt_key(crypt_key=crypt_key, password=password)

        self.folder().touch()
        if self.is_compressed():
            if self.is_encrypted():
                self._write_compressed_and_encrypted(data, crypt_key=crypt_key)
            else:
                self._write_compressed(data)
        elif self.is_encrypted():
            self._write_encrypted(data, crypt_key=crypt_key)
        else:
            self._write(data, mode=mode)

    def write_json(
        self,
        data: dict,
        human: bool = False,
        crypt_key: bytes | None = None,
        password: str | None = None,
        **kwargs,
    ):
        """
        Write dictionary to JSON file

        Extends :meth:`.JSON.dumps()` with :meth:`.File.write()`

        For encryption, use either ``crypt_key`` or ``password``. None or both
        will raise an exception. Encryption requires the file name to end with
        :data:`ENCRYPTED_EXTENSION`

        :raise FileError: If using ``crypt_key`` or ``password``, and the
            file does not have encrypted extension
        :param data: Data to write
        :type data: str or bytes
        :param human: If True, write JSON as human readable
        :type human: bool
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        """
        data = Serializer.json_dumps(data, human=human)
        self.write(data, mode="w", crypt_key=crypt_key, password=password)

    def write_yaml(
        self,
        data: dict,
        crypt_key: bytes | None = None,
        password: str | None = None,
        **kwargs,
    ):
        """
        Write dictionary to YAML file

        Extends :meth:`.YAML.dumps()` with :meth:`.File.write()`

        For encryption, use either ``crypt_key`` or ``password``. None or both
        will raise an exception. Encryption requires the file name to end with
        :data:`ENCRYPTED_EXTENSION`

        :raise FileError: If using ``crypt_key`` or ``password``, and the
            file does not have encrypted extension
        :param data: Data to write
        :type data: str or bytes
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        """
        data = Serializer.yaml_dumps(data)
        self.write(data, mode="w", crypt_key=crypt_key, password=password)

    def _write(self, data, mode="w"):
        with open(self, mode=mode) as f:
            f.write(data)

    def _write_compressed(self, content):
        if not isinstance(content, bytes):
            content = content.encode()
        with gzip.open(self, mode="wb") as f:
            f.write(content)

    def _write_encrypted(self, content, crypt_key=None):
        if not isinstance(content, bytes):
            content = content.encode()
        with open(self, mode="wb") as f:
            f.write(Crypt.encrypt(content, crypt_key))

    def _write_compressed_and_encrypted(self, content, crypt_key=None):
        if not isinstance(content, bytes):
            content = content.encode()
        with gzip.open(self, mode="wb") as f:
            f.write(Crypt.encrypt(content, crypt_key))

    def open(self, mode="r"):
        """
        Open file

        Returns a file handle by extending builtin ``open()``

        Intended use::

            fi = File("look_at_me.txt")
            with fi.open() as f:
                print(f.read())  # Do something more elaborate than this

            # This would also work (making this method rather useless)
            with open(fi) as f:
                print(f.read())

            # Better solution for this simple example
            print(fi.read())

        :param mode: File open mode
        :return: File handle
        """
        return open(self, mode=mode)

    def _is_binary(self, mode):
        return "b" in mode

    def readlines(self, num_lines=1):
        """
        Read lines in file

        Does not work with encrypted files

        Intended use is reading the header of a file

        :param num_lines: Number of lines to read. Default is 1
        :return: First line as a string if ``num_lines=1``, or a list of
            strings for each line
        :rtype: str or list
        """
        if PIXIE and self.is_encrypted():
            raise PixieInPipeline("Cannot read lines in encrypted file")
        if self.is_compressed():
            return self._readlines_compressed(num_lines=num_lines)
        else:
            return self._readlines(num_lines=num_lines)

    def read(
        self,
        mode="r",
        crypt_key: bytes | None = None,
        password: str | None = None,
        *args,
        **kwargs,
    ):
        """
        Read file

        If file is encrypted, use either ``crypt_key`` or ``password``.
        None or both will raise an exception. Encryption requires the file
        name to end with :data:`ENCRYPTED_EXTENSION`

        :raises FileError: If trying to decrypt a file without
            :data:`ENCRYPTED_EXTENSION`
        :param mode: Read mode
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        :return: Data as string or bytes depending on read mode
        :rtype: str or bytes
        """
        if not self.exists():
            raise FileError(f"Cannot read from file that does not exist: {self}")
        elif PIXIE and (crypt_key or password) and not self.is_encrypted():
            raise PixieInPipeline(
                f"File does not have crypt extension "
                f"({self.ENCRYPTED_EXTENSION}), "
                f"but a crypt_key "
                f"or password was sent as input to write."
            )
        if self.is_encrypted():
            crypt_key = self._crypt_key(crypt_key=crypt_key, password=password)

        if self.is_compressed():
            if self.is_encrypted():
                data = self._read_compressed_and_encrypted(crypt_key)
                if "b" not in mode:
                    data = data.decode()
            else:
                data = self._read_compressed(mode=mode)
                if "b" not in mode:
                    data = data.decode()
        else:
            if self.is_encrypted():
                data = self._read_encrypted(crypt_key=crypt_key)
                if "b" not in mode:
                    data = data.decode()
            else:
                data = self._read(mode=mode)

        return data

    def read_json(
        self,
        crypt_key: bytes | None = None,
        password: str | None = None,
        **kwargs,
    ):
        """
        Read json file

        Extends :meth:`.File.read()` with :meth:`.JSON.loads()`

        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        :return: Dictionary of JSON content
        :rtype: dict
        """
        data = self.read(mode="r", crypt_key=crypt_key, password=password)
        return Serializer.json_loads(data)

    def read_yaml(
        self,
        crypt_key: bytes | None = None,
        password: str | None = None,
        **kwargs,
    ):
        """
        Read json file

        Extends :meth:`.File.read()` with :meth:`.YAML.loads()`

        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        :return: Dictionary of YAML content
        :rtype: dict
        """
        data = self.read(mode="r", crypt_key=crypt_key, password=password)
        return Serializer.yaml_loads(data)

    def _read(self, mode="r"):
        with open(self, mode=mode) as f:
            return f.read()

    def _readlines(self, num_lines=1):
        with open(self) as f:
            content = []
            for n in range(num_lines):
                content.append(f.readline().strip())
            if len(content) == 1:
                return content[0]
        return content

    def _read_compressed(self, mode="rb"):
        with gzip.open(self, mode=mode) as f:
            return f.read()

    def _readlines_compressed(self, num_lines=1):
        with gzip.open(self, mode="rt") as f:
            content = []
            for n in range(num_lines):
                content.append(f.readline().strip())
        if not isinstance(content, str):
            if isinstance(content, list):
                for n in range(len(content)):
                    if isinstance(content[n], bytes):
                        content[n] = content[n].decode()  # type: ignore
            elif isinstance(content, bytes):
                content = content.decode()

        if len(content) == 1:
            return content[0]
        return content

    def _read_encrypted(self, crypt_key):
        data = self._read(mode="rb")
        decrypted = Crypt.decrypt(data, crypt_key)
        return decrypted

    def _read_compressed_and_encrypted(self, crypt_key):
        with gzip.open(self, mode="rb") as f:
            data = f.read()
        decrypted = Crypt.decrypt(data, crypt_key)
        return decrypted

    # def make_new_name(self,
    #                   stub,
    #                   extension,
    #                   is_hidden=False,
    #                   is_compressed=False,
    #                   is_encrypted=False):
    #     pass

    def rename(self, new_name: str):
        """
        Rename file

        :param new_name: New file name, including extension
        :type new_name: str
        :return: A file path with the new file name
        :rtype: File
        """
        new_path = str(self.join(self.folder(), new_name))
        os.rename(self, new_path)
        self._rename(new_path)

    def folder(self):
        """
        Get the folder containing the file

        :return: Folder containing the file
        :rtype: Folder
        """
        return Folder(os.path.dirname(self))

    def move(self, new_folder: Folder, new_name=None, overwrite: bool = False):
        """
        Move file to a new folder, and with an optional new name

        :param new_folder: New folder
        :type new_folder: Folder
        :param new_name: New file name (optional). If missing, the file will
            keep the same name
        :return: Moved file
        :rtype: File
        """
        if not self.exists():
            raise FileError(f"Cannot move non existent file: {self}")
        if PIXIE and not overwrite:
            if self.folder() == new_folder:
                if new_name and new_name == self.name():
                    raise FileError(f"Cannot move a file to the same name: {self}")
        new_folder.touch()
        if new_name:
            new_file = File.join(new_folder, new_name)
        else:
            new_file = File.join(new_folder, self.name())
        if not overwrite and new_file.exists():
            raise FileError(
                "Target file already exists. Use overwrite=True to allow overwrite"
            )
        shutil.move(self, new_file)
        self._rename(str(new_file))

    def copy(self, new_folder, new_name: str | None = None, overwrite: bool = False):
        """
        Copy file to a new folder, and optionally give it a new name

        :param overwrite: Set True to overwrite destination file if it exists
        :type overwrite: bool
        :param new_folder: New folder
        :type new_folder: Folder or str
        :param new_name: New file name (optional). If missing, the file will
            keep the same name
        :type new_name: str
        :return: Copied file
        :rtype: File
        """
        new_folder = Folder.glass(new_folder)
        if self.folder() == new_folder:
            raise FileError(f"Cannot copy a file to the same folder: {new_folder}")
        new_folder.touch()
        if new_name:
            new_file = File.join(new_folder, new_name)
        else:
            new_file = File.join(new_folder, self.name())
        if not overwrite and new_file.exists():
            raise FileError(
                f"Target file exists: {new_file}; Use overwrite=True to allow overwrite"
            )
        shutil.copyfile(self, new_file)
        return new_file

    def compress(self, delete_original: bool = True):
        """
        Compress file

        :param delete_original: If True, original file will be deleted after
            compression (default)
        :type delete_original: bool
        """
        if self.is_compressed():
            raise FileError(f"File already compressed: {self}")
        if self.is_encrypted():
            raise FileError(
                f"Cannot compress encrypted file: {self}. Decrypt file first"
            )

        self.logger.debug(f"Compress file: {self}")
        old_size = self.size()
        new_file = File(f"{self}.gz")
        if new_file.exists():
            self.logger.warning(f"Overwrite existing gz-file: {new_file}")
        with open(self, "rb") as f_in:
            with gzip.open(str(new_file), "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        if delete_original:
            self.delete()
        compression_percent = 100 * (old_size - new_file.size()) / old_size
        self.logger.debug(f"Compressed with compression {compression_percent:.2f} %")
        self._rename(str(new_file))

    def decompress(self, delete_original: bool = True, replace_if_exists: bool = True):
        """
        Decompress file

        :param delete_original: If True, the original compressed file will be
            deleted after decompression
        :type delete_original: bool
        :param replace_if_exists: If True, the decompressed file will replace
            any already existing file with the same name
        :type replace_if_exists: bool
        """
        if not self.is_compressed():
            raise FileError(f"File is not compressed: {self}")
        if self.is_encrypted():
            raise FileError(
                f"Cannot decompress encrypted file: {self}. Decrypt file first."
            )
        self.logger.debug(f"Decompress file: {self}")
        new_file = File(str(self).replace("." + self.COMPRESSED_EXTENSION, ""))
        if new_file.exists():
            if replace_if_exists:
                self.logger.debug(f"Overwrite existing file: {new_file}")
            else:
                raise FileError(
                    f"File already exists: '{new_file}'. "
                    f"Use replace_if_exists=True to ignore."
                )
        with gzip.open(self, "rb") as f_in:
            with open(new_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        if delete_original:
            self.delete()
        new_file = File.glass(new_file)
        # new_file.compression_percent = None
        self._rename(str(new_file))

    def encrypt(self, crypt_key: bytes, delete_original: bool = True):
        """
        Encrypt file

        :raise FileError: If file is already encrypted or if crypt_key is
            missing
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param delete_original: If True, the original unencrypted file will
            be deleted after encryption
        :type delete_original: bool
        """
        if self.is_encrypted():
            raise FileError(f"File is already encrypted: {self}")
        self.logger.debug(f"Encrypt file: {self}")
        encrypted_file = File(f"{self}.{self.ENCRYPTED_EXTENSION}")
        data = self._read(mode="rb")
        encrypted = Crypt.encrypt(data, crypt_key)
        encrypted_file._write(encrypted, mode="wb")
        if delete_original:
            self.delete()
        self._rename(str(encrypted_file))

    def decrypt(self, crypt_key: bytes, delete_original: bool = True):
        """
        Decrypt file

        :raise FileError: If file is not encrypted or if crypt_key is missing
        :param crypt_key: Encryption key
        :type crypt_key: bool
        :param delete_original: If True, the original encrypted file will
            be deleted after decryption
        :type delete_original: bool
        """
        if not self.is_encrypted():
            raise FileError(f"File is not encrypted: {self}")

        self.logger.debug(f"Decrypt file: {self}")
        decrypted_file = File(str(self).replace("." + self.ENCRYPTED_EXTENSION, ""))
        data = self._read(mode="rb")
        decrypted = Crypt.decrypt(data, crypt_key)
        decrypted_file._write(decrypted, mode="wb")
        if delete_original:
            self.delete()
        self._rename(str(decrypted_file))
