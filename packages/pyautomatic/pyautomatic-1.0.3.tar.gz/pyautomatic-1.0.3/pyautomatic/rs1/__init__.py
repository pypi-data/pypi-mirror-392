import base64
import hashlib
import os
import binascii
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
import secrets

def reverse_string(s):
    return s[::-1]

def string_to_ascii(s):
    return [ord(c) for c in s]

def ascii_to_binary(ascii_list):
    return [format(a, '08b') for a in ascii_list]

def binary_to_hex(binary_list):
    return [format(int(''.join(b), 2), '02x') for b in binary_list]

def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()

def md5_string(s):
    return hashlib.md5(s.encode()).hexdigest()

def encrypt(s, password=None):
    # 生成随机盐值和IV
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(16)
    
    # 如果没有提供密码，生成一个随机密码
    if password is None:
        password = secrets.token_urlsafe(32)
    
    # 使用PBKDF2派生密钥
    key = PBKDF2(password, salt, dkLen=32, count=100000)
    
    # 创建AES加密器
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 加密数据
    padded_data = pad(s.encode('utf-8'), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    
    # 组合所有数据
    encrypted_b64 = base64.b64encode(salt + iv + encrypted_data).decode('utf-8')
    
    # 计算哈希值用于验证
    hash_value = hashlib.sha256(s.encode()).hexdigest()
    
    return f"{encrypted_b64}:{hash_value}"

def decrypt(encrypted_data, password=None):
    try:
        # 分割数据
        encrypted_b64, stored_hash = encrypted_data.split(':')
        
        # 解码Base64数据
        data = base64.b64decode(encrypted_b64)
        
        # 提取盐值、IV和加密数据
        salt = data[:16]
        iv = data[16:32]
        encrypted = data[32:]
        
        # 如果没有提供密码，抛出异常
        if password is None:
            raise ValueError("解密需要密码")
        
        # 派生密钥
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        
        # 创建解密器
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # 解密数据
        decrypted_padded = cipher.decrypt(encrypted)
        decrypted = unpad(decrypted_padded, AES.block_size)
        result = decrypted.decode('utf-8')
        
        # 验证哈希值
        computed_hash = hashlib.sha256(result.encode()).hexdigest()
        if computed_hash != stored_hash:
            raise ValueError("数据完整性验证失败")
        
        return result
        
    except Exception as e:
        raise ValueError(f"解密失败: {str(e)}")

if __name__ == "__main__":
    original = "zzz.8848"
    password = "8848"
    
    # 加密
    encrypted = encrypt(original, password)
    print("加密结果:", encrypted)
    
    # 解密

    decrypted = decrypt(encrypted, password)
    print("解密结果:", decrypted)