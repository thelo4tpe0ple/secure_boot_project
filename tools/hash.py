import hashlib
from typing import Optional, Union

class ESPImageHash:
    """
    ESP 固件 SHA-256 摘要提取与验证工具。
    不依赖于段解析，直接操作原始二进制数据。
    """

    def __init__(self, raw_data: bytes, hash_appended: bool = False):
        """
        :param raw_data: 固件文件的全部字节数据
        :param hash_appended: 是否包含 SHA-256 摘要（通常来自扩展头）
        """
        self.raw_data = raw_data
        self.hash_appended = hash_appended
        self.digest: Optional[bytes] = None
        self._extract_digest()

    def _extract_digest(self):
        """从文件末尾提取 SHA-256 摘要（仅当长度足够且 hash_appended 为 True）"""
        if not self.hash_appended:
            self.digest = None
            return

        # 检查文件大小是否至少包含 32 字节摘要
        if len(self.raw_data) < 32:
            self.digest = None
            return

        # 假设摘要位于文件末尾 32 字节
        self.digest = self.raw_data[-32:]

    def verify(self) -> bool:
        """
        验证 SHA-256 摘要是否正确。
        计算范围为：整个文件除去末尾 32 字节（如果存在摘要）。
        """
        if self.digest is None:
            return False

        # 确定待哈希的数据范围
        if self.hash_appended and len(self.raw_data) >= 32:
            data_to_hash = self.raw_data[:-32]
        else:
            # 如果没有摘要，则对整个文件进行哈希（但 verify 应返回 False）
            return False

        calculated = hashlib.sha256(data_to_hash).digest()
        return calculated == self.digest

    @classmethod
    def from_file(cls, filename: str, hash_appended: bool = False) -> 'ESPImageHash':
        """从文件创建实例"""
        with open(filename, 'rb') as f:
            raw = f.read()
        return cls(raw, hash_appended)