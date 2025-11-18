import base64
import os
import random
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PBKDF2Fernet:
    def __init__(
        self,
        password: str | None = None,
        safe_salt: str | None = None,
        iterations: int | None = None,
    ):
        if password is None:
            password = self.rand_letter(32)
        self.password = password
        if safe_salt is None:
            self.salt = os.urandom(16)
            self.safe_salt = self.bytes_to_url64str(self.salt)
        else:
            self.salt = self.url64str_to_bytes(safe_salt)
            self.safe_salt = safe_salt

        if iterations is None:
            self.iterations = random.randint(100, 100000)
        else:
            self.iterations = iterations
        self.key = self._generate_pbkdf2_fernet_key(
            self.password.encode("utf-8"), self.salt, self.iterations
        )
        self.fernet = Fernet(self.key)

    @staticmethod
    def rand_letter(n: int):
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    @staticmethod
    def bytes_to_url64str(url64str: bytes):
        s = base64.urlsafe_b64encode(url64str).rstrip(b"=").decode("utf-8")
        return s

    @staticmethod
    def url64str_to_bytes(s):
        _, r = divmod(len(s), 4)
        url64str = base64.urlsafe_b64decode((s + "=" * r).encode("utf-8"))
        return url64str

    def _generate_pbkdf2_fernet_key(
        self, password: bytes, salt: bytes, iterations: int = 100000
    ) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt(self, data: bytes) -> bytes:
        return self.fernet.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:
        return self.fernet.decrypt(token)
