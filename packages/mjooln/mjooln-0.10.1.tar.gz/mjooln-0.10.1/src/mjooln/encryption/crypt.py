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

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from mjooln.exception import CryptError


class Crypt:
    """Wrapper for best practice key generation and AES 128 encryption

    From `Fernet Docs <https://cryptography.io/en/latest/fernet/>`_:
    HMAC using SHA256 for authentication, and PKCS7 padding.
    Uses AES in CBC mode with a 128-bit key for encryption, and PKCS7 padding.
    """

    # TODO: Do QA on cryptographic strength

    @classmethod
    def generate_key(cls) -> bytes:
        """Generates URL-safe base64-encoded random key with length 44"""
        return Fernet.generate_key()

    @classmethod
    def salt(cls) -> bytes:
        """Generates URL-safe base64-encoded random string with length 24

        :return: bytes
        """

        # Used 18 instead of standard 16 since encode otherwise leaves
        # two trailing equal signs (==) in the resulting string
        return base64.urlsafe_b64encode(os.urandom(18))

    @classmethod
    def key_from_password(cls, salt: bytes, password: str) -> bytes:
        """Generates URL-safe base64-encoded random string with length 44

        :type salt: bytes
        :type password: str
        :return: bytes
        """

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @classmethod
    def encrypt(cls, data: bytes, key: bytes) -> bytes:
        """Encrypts input data with the given key

        :type data: bytes
        :type key: bytes
        :return: bytes
        """
        if key is None:
            raise CryptError("Encryption key missing, cannot encrypt")
        fernet = Fernet(key)
        return fernet.encrypt(data)

    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> bytes:
        """Decrypts input data with the given key

        :type data: bytes
        :type key: bytes
        :return: bytes
        """
        if key is None:
            raise CryptError("Encryption key missing, cannot encrypt")
        fernet = Fernet(key)
        try:
            return fernet.decrypt(data)
        except InvalidToken as it:
            raise CryptError(
                f"Invalid token. Probably due to "
                f"invalid password/key. Actual message: {it}"
            )
