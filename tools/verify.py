import hashlib
from typing import Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key


# ========== 哈希相关函数 ==========

def compute_sha256(data: bytes) -> bytes:
    """计算二进制数据的 SHA‑256 摘要，返回原始字节（32 字节）"""
    return hashlib.sha256(data).digest()


def save_digest(digest: bytes, file_path: str) -> None:
    """将摘要原始字节保存到文件（如 firmware.sha256）"""
    with open(file_path, 'wb') as f:
        f.write(digest)


def load_digest(file_path: str) -> Optional[bytes]:
    """从文件加载摘要原始字节，若文件不存在则返回 None"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None


# ========== 签名验证函数 ==========

def verify_signature(data: bytes, signature: bytes, public_key_path: str, key_type: str = 'ec') -> bool:
    """
    验证固件签名
    :param data: 固件原始字节
    :param signature: 从 .sig 文件读取的签名
    :param public_key_path: PEM 格式公钥文件路径
    :param key_type: 'ec' 或 'rsa'
    :return: True 验证通过，False 失败
    """
    digest = compute_sha256(data)  # 使用本模块的哈希函数
    with open(public_key_path, 'rb') as f:
        public_key = load_pem_public_key(f.read(), backend=default_backend())

    try:
        if key_type == 'ec':
            public_key.verify(signature, digest, ec.ECDSA(hashes.SHA256()))
        elif key_type == 'rsa':
            public_key.verify(signature, digest, padding.PKCS1v15(), hashes.SHA256())
        else:
            raise ValueError("Unsupported key_type, use 'ec' or 'rsa'")
        return True
    except Exception:
        return False