import dataclasses
import re
import struct

from .bbi_locs import ChrItem
from .util import read_until

BIGWIG_MAGIC = 0x888FFC26
BIGBED_MAGIC = 0x8789F2EB
BIGWIG_MAGIC_SWAPPED = 0x26FC8F88
BIGBED_MAGIC_SWAPPED = 0xEBF28987

CHR_TREE_MAGIC = 0x78CA8C91
CHR_TREE_MAGIC_SWAPPED = 0x91CA8C78

BBI_MIN_VERSION = 3
BBI_OUTPUT_VERSION = 4


@dataclasses.dataclass
class BBIHeader:
    magic: int
    version: int
    zoom_levels: int
    chr_tree_offset: int
    full_data_offset: int
    full_index_offset: int
    field_count: int
    defined_field_count: int
    auto_sql_offset: int
    total_summary_offset: int
    uncompress_buffer_size: int
    reserved: int


@dataclasses.dataclass
class ZoomHeader:
    reduction_level: int
    reserved: int
    data_offset: int
    index_offset: int


@dataclasses.dataclass
class TotalSummary:
    bases_covered: int
    min_value: float
    max_value: float
    sum_data: float
    sum_squared: float


@dataclasses.dataclass
class ChrTreeHeader:
    magic: int
    block_size: int
    key_size: int
    value_size: int
    item_count: int
    reserved: int


@dataclasses.dataclass
class DataTreeHeader:
    magic: int
    block_size: int
    item_count: int
    start_chr_index: int
    start_base: int
    end_chr_index: int
    end_base: int
    end_file_offset: int
    items_per_slot: int
    reserved: int


def read_bbi_header(file):
    file.seek(0)
    buffer = file.read(64)
    magic = struct.unpack("<I", buffer[0:4])[0]
    if magic != BIGWIG_MAGIC and magic != BIGBED_MAGIC:
        if magic == BIGWIG_MAGIC_SWAPPED or magic == BIGBED_MAGIC_SWAPPED:
            raise RuntimeError("incompatible endianness")
        raise RuntimeError("not a bigwig or bigbed file")
    version = struct.unpack("<H", buffer[4:6])[0]
    if version < BBI_MIN_VERSION:
        raise RuntimeError(f"bigwig or bigbed version {version} unsupported (>= {BBI_MIN_VERSION})")
    return BBIHeader(magic, version, *struct.unpack("<HQQQHHQQIQ", buffer[6:64]))


def read_zoom_headers(file, zoom_levels):
    headers = []
    if zoom_levels == 0:
        return headers
    file.seek(64)
    buffer = file.read(zoom_levels * 24)
    for i in range(zoom_levels):
        header = ZoomHeader(*struct.unpack("<IIQQ", buffer[i * 24:i * 24 + 24]))
        headers.append(header)
    return headers


def read_auto_sql(file, offset, field_count):
    if offset == 0:
        return {}
    file.seek(offset)
    sql_string = str(read_until(file, b"\0"))
    fields = {}
    re_field = re.compile(r'\s*(\S+)\s+([^;]+);')
    for line in sql_string.splitlines():
        match = re_field.match(line)
        if match:
            type = match.group(1)
            field_list = match.group(2)
            re_name = re.compile(r'\s*(\S+)\s*(?:,|$)')
            for name_match in re_name.finditer(field_list):
                name = name_match.group(1)
                if name:
                    fields[name] = type
    if (len(fields) < 3 or
        not re.match(r'^(chr(?:om)_?(?:id|name)?)$', list(fields.keys())[0], re.IGNORECASE) or
        not re.match(r'^(?:chr(?:om)?_?)?start$', list(fields.keys())[1], re.IGNORECASE) or
        not re.match(r'^(?:chr(?:om)?_?)?end$', list(fields.keys())[2], re.IGNORECASE)):
        raise RuntimeError("missing or misplaced chr, start or end in autosql")
    if len(fields) != field_count:
        raise RuntimeError(f"field count {field_count} does not match autosql field count {len(fields)}")
    return fields


def read_total_summary(file, offset):
    file.seek(offset)
    buffer = file.read(40)
    return TotalSummary(*struct.unpack("<Qdddd", buffer))


def read_chr_tree_header(file, offset):
    file.seek(offset)
    buffer = file.read(32)
    magic = struct.unpack("<I", buffer[0:4])[0]
    if magic != CHR_TREE_MAGIC:
        if magic == CHR_TREE_MAGIC_SWAPPED:
            raise RuntimeError("incompatible endianness (chromosome tree)")
        raise RuntimeError("invalid chr tree magic number")
    return ChrTreeHeader(magic, *struct.unpack("<IIIQQ", buffer[4:32]))


def read_chr_list(file, offset, key_size):
    items = []
    file.seek(offset)
    header_buffer = file.read(4)
    is_leaf = struct.unpack("<B", header_buffer[0:1])[0]
    # reserved = struct.unpack("<B", header_buffer[1:2])[0]
    count = struct.unpack("<H", header_buffer[2:4])[0]
    buffer = file.read(count * (key_size + 8))
    for i in range(count):
        buffer_index = i * (key_size + 8)
        if is_leaf:
            key = buffer[buffer_index:buffer_index + key_size]
            key = key.rstrip(b"\0").decode()
            index, size = struct.unpack("<II", buffer[buffer_index + key_size:buffer_index + key_size + 8])
            item = ChrItem(key, index, size)
            items.append(item)
        else:
            # key = buffer[buffer_index:buffer_index + key_size]
            child_offset = struct.unpack("<Q", buffer[buffer_index + key_size:buffer_index + key_size + 8])[0]
            child_items = read_chr_list(file, child_offset, key_size)
            items.extend(child_items)
    items.sort(key=lambda x: x.index)
    return items
