import textwrap
from getpass import getpass
from .pbkdf_fernet import PBKDF2Fernet

SPLIT_TAG = "=SPLIT.HERE="
HIDDEN_PASSWORD_TAG = "-"

class TxtFileCipher:
    """Class to encrypt/decrypt text files with PBKDF2Fernet.
    """
    def __init__(self):
        pass

    @staticmethod
    def str_from_txtfile(fin) -> str:
        with open(fin, encoding="utf-8") as f:
            s = f.read()
        return s

    @staticmethod
    def str_to_txtfile(s: str, fout=None):
        if fout is None:
            print(s)
        else:
            with open(fout, "w", encoding="utf-8") as f:
                f.write(s)

    @staticmethod
    def split_str_to_list(s, nlength=80):
        lines = textwrap.wrap(s, nlength)
        return lines


    def encrypt_str_to_list(self,s: str, password=None):
        cryptor = PBKDF2Fernet(password=password)
        encrypted_data = cryptor.encrypt(s.encode("utf-8"))
        safe_data = cryptor.bytes_to_url64str(encrypted_data)
        lines = [cryptor.password, cryptor.safe_salt, str(cryptor.iterations)]
        lines.extend(self.split_str_to_list(safe_data))
        return lines


    def decrypt_list_to_str(self,list_in, password=None) -> str:
        _password, safe_salt, _iterations, *_data = list_in
        if _password == HIDDEN_PASSWORD_TAG:
            if password is None:
                raise ValueError("Password is required for decryption")
            else:
                _password = password
        iterations = int(_iterations)
        decryptor = PBKDF2Fernet(
            password=_password, safe_salt=safe_salt, iterations=iterations
        )
        s = "".join(_data)
        decrypted_bytes = decryptor.decrypt(decryptor.url64str_to_bytes(s))
        return decrypted_bytes.decode("utf-8")
    
    def encrypt_txtfile(self, fin, fout=None, password=None, skip_password=False):
        """encrypt text file.
        example::

            encrypt_txtfile("test.txt")  # output to print, password input
            encrypt_txtfile("test.txt", "test.txt.enc") # output to test.txt.enc
            encrypt_txtfile("test.txt", password="mypassword")
            encrypt_txtfile("test.txt", skip_password=True)  # skip password input, use random password
            encrypt_txtfile("test.txt", fout=".")  # output to test.txt_1

        output format::

            <original file content>
            =SPLIT.HERE=
            prompt password=...
            salt=...
            iterations=...
            -<encrypted content>
        """
        s = self.str_from_txtfile(fin)
        s_list = s.split("\n")
        find = False
        for i, line in enumerate(s_list):
            if line.strip() == SPLIT_TAG:
                head_list = s_list[: i + 1]
                raw_list = s_list[i + 1 :]
                find = True
                break
        if not find:
            head_list = [fin, SPLIT_TAG]
            raw_list = s_list

        if password is None:
            if not skip_password:
                password = getpass("input password (empty for random) = ")

        s_raw = "\n".join(raw_list)

        if password:
            encrypted_list = self.encrypt_str_to_list(s_raw, password)
            encrypted_list[0] = HIDDEN_PASSWORD_TAG
        else:
            encrypted_list = self.encrypt_str_to_list(s_raw)

        s_out = "\n".join(head_list + encrypted_list)

        if fout == ".":
            fout = fin + "_1"

        self.str_to_txtfile(s_out, fout)


    def decrypt_txtfile(self, fin, fout=None, password=None):
        """decrypt text file.
        examples::

            decrypt_txtfile("test.txt")  # output to print
            decrypt_txtfile("test.txt", password="mypassword")
            decrypt_txtfile("test.txt", fout=".")  # output to test.txt_2
            decrypt_txtfile("test.txt", "test.txt.dec")  # output to test.txt.dec
        """
        s = self.str_from_txtfile(fin)
        s_list = s.split("\n")
        find = False
        prompts = []
        for i, line in enumerate(s_list):
            if line.startswith("prompt"):
                prompts.append(line)
            if line.strip() == SPLIT_TAG:
                head_list = s_list[: i + 1]
                encrypted_list = s_list[i + 1 :]
                find = True
                break
        if not find:
            raise ValueError(f"Cannot find split tag '{SPLIT_TAG}' in file '{fin}'")

        if encrypted_list[0] == "-" and password is None:
            print("\n".join(prompts))
            password = getpass("input password=")

        if password is None:
            s2 = self.decrypt_list_to_str(encrypted_list)
        else:
            s2 = self.decrypt_list_to_str(encrypted_list, password)

        s_out = "\n".join(head_list + [s2])

        if fout == ".":
            fout = fin + "_2"
        self.str_to_txtfile(s_out, fout)
