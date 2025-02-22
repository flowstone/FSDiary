from cryptography.fernet import Fernet

class EncryptionUtil:
    @staticmethod
    def generate_key(file_path):
        key = Fernet.generate_key()
        with open(file_path, "wb") as file:
            file.write(key)
    # 加密
    @staticmethod
    def encrypt(data, key):
        fernet = Fernet(key)
        return fernet.encrypt(data)


    # 解密
    @staticmethod
    def decrypt(data, key):
        fernet = Fernet(key)
        return fernet.decrypt(data)
