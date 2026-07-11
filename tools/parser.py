import hashlib
from dataclasses import dataclass
import struct
from hash import ESPImageHash
from typing import AnyStr, List


@dataclass
class ImageHeader:
    magic:int
    segment_count:int
    flash_mode:int
    flash_size_freq:int
    entry_addr: int

@dataclass
class SegmentHeader:
    load_addr:int
    data_len:int

@dataclass
class Segment:
    header: SegmentHeader
    data: bytes   # 原始二进制数据

class ESPImageParser:

    def __init__(self, filename):
        self.filename = filename
        with open(self.filename,'rb') as f:
            self.raw_data = f.read()
        self.header: ImageHeader = None
        self.extended_header = None
        self.segments: List[Segment] = []
        self.parse_header()
        self.parse_segments()
        self.parse_footer()
        self.hash = ESPImageHash(
            self.raw_data,
            hash_appended=True)

    def parse_header(self):
        if len(self.raw_data)<24:
            raise ValueError("文件大小不足24字节，不是有效的ESP固件")
        head = self.raw_data[:24]
        self.magic = head[0]
        self.segment_count = head[1]  # 1字节
        self.flash_mode = head[2]
        self.flash_size_freq = head[4]
        # 第7字节是填充，忽略
        self.entry_addr = struct.unpack('<I', head[6:10])[0]
        if self.magic != 0xE9:
            raise ValueError("无效的固件magic数")
        self.header = ImageHeader(
            magic = self.magic,
            segment_count=self.segment_count,
            flash_mode=self.flash_mode,
            flash_size_freq=self.flash_size_freq,
            entry_addr= self.entry_addr
        )
    def parse_segments(self):
        offset = 24
        self.segments = []
        for _ in range(self.segment_count):
            if offset+8>len(self.raw_data):
                raise ValueError("文件中segment header长度被截断，无法读取")
            self.load_addr,self.data_len = struct.unpack('<II',self.raw_data[offset:offset+8])#读取segment header数据
            offset+=8
            if offset+self.data_len>len(self.raw_data):
                raise ValueError("段长度超出文件范围")
            self.segment_data = self.raw_data[offset:offset+self.data_len]
            offset+=self.data_len
            self.segment_header = SegmentHeader(load_addr=self.load_addr,data_len=self.data_len)
            self.segments.append(Segment(header = self.segment_header,data = self.segment_data))
            self.footer_offset = offset

    def parse_footer(self):
        offset = self.footer_offset
        raw_data = self.raw_data

        padding_len = (16-(offset%16)-1)%16
        offset += padding_len

        if offset>= len(raw_data):
            self.checksum = None
        else:
            self.checksum = raw_data[offset]


    def dump(self,output_filename:str=None):
        if output_filename is None:
            output_filename = self.filename + "_dump.txt"
        with open(output_filename,'w',encoding='utf-8') as f:
            # 写入头部信息
            f.write("========== Image Header ==========\n")
            f.write(f"Magic: 0x{self.header.magic:08X}\n")
            f.write(f"Segment Count: {self.header.segment_count}\n")
            f.write(f"Flash Mode: 0x{self.header.flash_mode:02X}\n")
            f.write(f"Flash Size/Freq: 0x{self.header.flash_size_freq:02X}\n")
            f.write(f"Entry Address: 0x{self.header.entry_addr:08X}\n")
            f.write("\n")
            for idx,seg in enumerate(self.segments):
                f.write(f"========== Segment {idx+1} ==========\n")
                f.write(f"Load Address: 0x{seg.header.load_addr:08X}\n")
                f.write(f"Data Length: {seg.header.data_len} bytes\n")
                f.write("Data (hex):\n")
                data = seg.data
                for i in range(0,len(data),16):
                    chunk = data[i:i+16]
                    hex_str = ' '.join(f'{b:02X}' for b in chunk)
                    f.write(f"  {i:04X}: {hex_str}\n")
                f.write("\n")
            f.write(f"Checksum: 0x{self.checksum:02X}\n")
            f.write(f"SHA-256 Digest: {self.hash.digest.hex() if self.hash.digest else 'Not Present'}\n")
            f.write(f"SHA-256 Verified: {self.hash.verify()}\n")

    def verify_sha256(self):
        return self.hash.verify()
if __name__ == "__main__":
    parser = ESPImageParser("../blink/build/blink.bin")
    parser.dump()
    res = parser.verify_sha256()
    if res:
        print("check pass")
