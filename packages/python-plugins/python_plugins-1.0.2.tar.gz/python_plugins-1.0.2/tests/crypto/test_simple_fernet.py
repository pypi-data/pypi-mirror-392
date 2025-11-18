import pytest
import os
import base64

from python_plugins.crypto.simple_fernet import SimpleFernet


class TestSimpleFernet:
    @pytest.mark.parametrize(
        "input_key, expected",
        [
            (None, 32),
            ("", 32),
            ("world", 32),
            ("abc" * 40, 32),
            (os.urandom(16), 32),
            (os.urandom(40), 32),
        ],
    )
    def test_random_secret_token(self, input_key, expected):
        sf = SimpleFernet(input_key)
        decode_key = base64.urlsafe_b64decode(sf.key)
        # print(sf.key, decode_key)
        assert len(decode_key) == expected

    def test_encrypt_decrypt(self, fake):
        sf = SimpleFernet()
        txt = "abc123!@#"
        token = sf.encrypt(txt)
        # print(token)
        assert isinstance(token, str)
        decrypt_txt = sf.decrypt(token)
        # print(decrypt_txt)
        assert isinstance(decrypt_txt, str)
        assert txt == decrypt_txt

    def test_encrypt_decrypt_with_key(self):
        f = SimpleFernet("my_secret_key")
        encrypted = f.encrypt("Hello, World!")
        decrypted = f.decrypt(encrypted)
        assert decrypted == "Hello, World!"
