import base64
from cryptography.hazmat.primitives import padding
from cryptography.fernet import Fernet


class SimpleFernet:
    """A simple wrapper around cryptography.fernet.Fernet for encryption and decryption.

    Args:
    
        key (str | bytes | None): The key used for encryption and decryption. If None, a new key will be generated.

    examples:

        >>> fernet = SimpleFernet("my_secret_key")
        >>> encrypted = fernet.encrypt("Hello, World!")
        >>> decrypted = fernet.decrypt(encrypted)
        >>> assert decrypted == "Hello, World!"
    """
    def __init__(self, key: str | bytes | None = None):
        self.key = self._generate_key(key)
        self.fernet = Fernet(self.key)

    def _generate_key(self, key: str | bytes | None) -> bytes:
        """Generate a Fernet key from a given string or bytes.
        see cryptography.fernet.Fernet.generate_key() for details.
        """
        if key is None:
            return Fernet.generate_key()

        if isinstance(key, str):
            key = key.encode("utf-8")
        # Fernet key must be 32 bytes.
        if len(key) < 32:
            padder = padding.PKCS7(32 * 8).padder()
            fernet_key = padder.update(key) + padder.finalize()
        else:
            fernet_key = key[0:32]
        return base64.urlsafe_b64encode(fernet_key)

    def encrypt(self, data: str | bytes) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")
        token = self.fernet.encrypt(data)
        return token.decode("utf-8")

    def decrypt(self, data: str | bytes) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")
        decrypt_data = self.fernet.decrypt(data)
        return decrypt_data.decode("utf-8")
