import pytest
import os
import os.path as op
import filecmp
import random
import string
from python_plugins.crypto.txtfile_cipher import TxtFileCipher
from python_plugins.crypto.txtfile_cipher import SPLIT_TAG

tmp_path = op.join(os.path.dirname(os.path.abspath(__file__)), "tmp")

path_1 = op.join(tmp_path, "test1.txt")
path_2 = op.join(tmp_path, "test2.txt")
path_3 = op.join(tmp_path, "test3.txt")
path_4 = op.join(tmp_path, "test4.txt")
path_5 = op.join(tmp_path, "test5.txt")


def rand_sentence(n):
    return "".join(
        random.choices(string.ascii_letters + string.digits + " " * 10, k=n)
    ).strip()


def _create_temp():
    if not op.exists(tmp_path):
        os.mkdir(tmp_path)
        return tmp_path


def _create_rand_file(path):
    with open(path, "w") as f:
        f.write(rand_sentence(30))
        f.write("\n")
        f.write(SPLIT_TAG)
        f.write("\n")
        f.write(rand_sentence(30))


def _create_fix_file(path):
    with open(path, "w") as f:
        f.write("abcdefghijklmnopqrstuvwxyz")
        f.write("\n")
        f.write("0123456789")


def safe_delete(path):
    try:
        if op.exists(path):
            os.remove(path)
    except:
        pass


def _remove_testfiles():
    safe_delete(path_1)
    safe_delete(path_2)
    safe_delete(path_3)
    safe_delete(path_4)
    safe_delete(path_5)


def test_crypto_file():
    create_tmp = _create_temp()
    if create_tmp:
        print(create_tmp)

    _create_fix_file(path_1)

    ctf = TxtFileCipher()
    ctf.encrypt_txtfile(path_1, path_2, skip_password=True)
    # decrypt_txtfile(path_2)
    ctf.decrypt_txtfile(path_2, path_3)
    with open(path_1, "r") as f1, open(path_3, "r") as f3:
        content_1 = f1.read()
        content_3 = f3.read()

    lines_1 = content_1.splitlines()
    lines_3 = content_3.splitlines()
    assert lines_3[0] == path_1
    assert lines_3[1] == SPLIT_TAG
    for i, line in enumerate(lines_1):
        assert line == lines_3[i + 2]

    _remove_testfiles()


def test_crypto_file_with_split():
    create_tmp = _create_temp()
    if create_tmp:
        print(create_tmp)

    _create_rand_file(path_1)

    ctf = TxtFileCipher()
    ctf.encrypt_txtfile(path_1, path_2, skip_password=True)
    # ctf.decrypt_txtfile(path_2)
    ctf.decrypt_txtfile(path_2, path_3)
    cmp_result = filecmp.cmp(path_1, path_3)
    assert cmp_result is True

    _remove_testfiles()


def test_crypto_file_with_password():

    _create_rand_file(path_1)
    ctf = TxtFileCipher()
    password = rand_sentence(10)
    ctf.encrypt_txtfile(path_1, path_2, password=password)
    with pytest.raises(Exception):
        ctf.decrypt_txtfile(path_2, path_3, password="")
    ctf.decrypt_txtfile(path_2, path_3, password=password)
    cmp_result = filecmp.cmp(path_1, path_3)
    assert cmp_result is True

    _remove_testfiles()


# pytest with `input()` must using `-s`
# pytest tests\test_crypt_file.py::test_crypto_file_with_password -s
@pytest.mark.skip
def test_crypto_file_with_input_password():

    _create_rand_file(path_1)

    ctf = TxtFileCipher()
    ctf.encrypt_txtfile(path_1, path_2)
    ctf.decrypt_txtfile(path_2, path_3)
    cmp_result = filecmp.cmp(path_1, path_3)
    assert cmp_result is True

    _remove_testfiles()
