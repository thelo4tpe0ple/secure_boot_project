import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# 导入 verify 中的哈希函数，保持唯一来源
from verify import compute_sha256


def sign_data(data: bytes, private_key_path: str, key_type: str = 'ec') -> bytes:
    """
    对固件数据进行签名（内部先计算 SHA‑256 摘要）
    :param data: 固件原始字节
    :param private_key_path: PEM 格式私钥文件路径
    :param key_type: 'ec' 或 'rsa'
    :return: 签名原始字节
    """
    digest = compute_sha256(data)  # 使用统一的哈希函数
    with open(private_key_path, 'rb') as f:
        private_key = load_pem_private_key(f.read(), password=None, backend=default_backend())

    if key_type == 'ec':
        signature = private_key.sign(digest, ec.ECDSA(hashes.SHA256()))
    elif key_type == 'rsa':
        signature = private_key.sign(digest, padding.PKCS1v15(), hashes.SHA256())
    else:
        raise ValueError("Unsupported key_type, use 'ec' or 'rsa'")
    return signature


def save_signature(signature: bytes, file_path: str) -> None:
    with open(file_path, 'wb') as f:
        f.write(signature)