import random
import string
import os
import base64
import uuid
import secrets

# random.sample  # unique
# random.choices # not unique


class RandomStringGenerator:
    """随机字符串生成器类"""

    @staticmethod
    def digits(n=6):
        """随机数字"""
        return "".join(random.choices(string.digits, k=n))

    @staticmethod
    def letters(n: int):
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    @staticmethod
    def sentence(n):
        return "".join(
            random.choices(string.ascii_letters + string.digits + " " * 10, k=n)
        ).strip()

    @staticmethod
    def uuid4():
        return str(uuid.uuid4())

    @staticmethod
    def token():
        return uuid.uuid4().hex

    @staticmethod
    def secret_token():
        return secrets.token_hex(32)

    @staticmethod
    def secret_token_16():
        return secrets.token_hex(16)

    def rand_token_2(n):
        # replace '+/' with '1a'
        token = base64.b64encode(os.urandom(n), b"1a").decode()[0:n]
        return token

    @staticmethod
    def simple(length=10):
        """简单随机字符串"""
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(length))

    @staticmethod
    def secure(length=16):
        """安全随机字符串"""
        chars = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def alphabetic(length=8, case="both"):
        """字母字符串"""
        if case == "upper":
            chars = string.ascii_uppercase
        elif case == "lower":
            chars = string.ascii_lowercase
        else:
            chars = string.ascii_letters
        return "".join(random.choice(chars) for _ in range(length))


# 使用示例
generator = RandomStringGenerator()

print("简单随机:", generator.simple(12))
print("安全密码:", generator.secure(20))
print("数字验证码:", generator.digits(6))
print("大写字母:", generator.alphabetic(8, "upper"))
print("小写字母:", generator.alphabetic(8, "lower"))
print("混合字母:", generator.alphabetic(10))
