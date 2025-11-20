import rs1

if __name__ == '__main__':
    encrypted = input("请输入密钥：")  # "le4eKlZwatCQSFYepHp9XzBKlVqJBmx+foRGOz4076w3JFNilgqAUlIvY6ErrsnzjqZIDjvcy4mRIKnYLa7Cwg==:a6eda4f443c9158ee5172bd8489684df422752f898655d0db2139a7dc67dcd77"
    password = input("请输入密码：")  # zzz.8848
    decrypted = rs1.decrypt(encrypted, password)
    print("解密结果:", decrypted)