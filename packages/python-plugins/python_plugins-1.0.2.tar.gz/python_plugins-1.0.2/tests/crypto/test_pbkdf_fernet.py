import os
import pytest
from python_plugins.crypto.pbkdf_fernet import PBKDF2Fernet


class TestPBKDF2Fernet:
    def test_rand_letter_length_and_alnum(self):
        s = PBKDF2Fernet.rand_letter(32)
        assert isinstance(s, str)
        assert len(s) == 32
        assert s.isalnum()

    def test_bytes_url64_roundtrip(self):
        data = os.urandom(100)
        s = PBKDF2Fernet.bytes_to_url64str(data)
        back = PBKDF2Fernet.url64str_to_bytes(s)
        assert back == data

    def test_deterministic_key_for_same_parameters(self):
        password = "samepass"
        iterations = 2000
        # use a fixed salt
        salt = os.urandom(16)
        safe_salt = PBKDF2Fernet.bytes_to_url64str(salt)

        a = PBKDF2Fernet(password=password, safe_salt=safe_salt, iterations=iterations)
        assert isinstance(a.password, str)
        assert isinstance(a.key, bytes)
        b = PBKDF2Fernet(password=password, safe_salt=safe_salt, iterations=iterations)
        # the underlying Fernet key (base64 urlsafe) should be identical
        assert a.key == b.key
        assert a.password == b.password


    def test_encrypt_decrypt_roundtrip(self):
        password = "test-password-123"

        # create first instance (will generate salt if not provided)
        a = PBKDF2Fernet(password=password)
        # reuse exact safe_salt and parameters to create a second instance
        b = PBKDF2Fernet(
            password=password, safe_salt=a.safe_salt, iterations=a.iterations
        )

        payload = b"the quick brown fox"
        token = a.encrypt(payload)
        assert isinstance(token, (bytes,))

        recovered = b.decrypt(token)
        assert recovered == payload


