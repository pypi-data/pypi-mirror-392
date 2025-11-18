import dataclasses
import struct
import zlib


@dataclasses.dataclass
class WigDataHeader:
    chr_index: int
    chr_start: int
    chr_end: int
    item_step: int
    item_span: int
    type: int
    reserved: int
    item_count: int


@dataclasses.dataclass
class ZoomDataRecord:
    chr_index: int
    chr_start: int
    chr_end: int
    valid_count: int
    min_value: float
    max_value: float
    sum_data: float
    sum_squared: float


def read_wig_data_header(buffer):
    """Read WigData header from buffer."""
    return WigDataHeader(*struct.unpack("<IIIIIBBH", buffer[0:24]))


def read_zoom_data_record(buffer, offset):
    """Read ZoomData record from buffer at offset."""
    return ZoomDataRecord(*struct.unpack("<IIIIffff", buffer[offset:offset + 32]))


@dataclasses.dataclass
class DataInterval:
    chr_index: int
    start: int
    end: int
    value: float


def iter_data_intervals(file, data_tree_item, locs, locs_interval, zoom_level, uncompress_buffer_size):
    index = 0
    file.seek(data_tree_item.data_offset)
    buffer = file.read(data_tree_item.data_size)
    if uncompress_buffer_size > 0:
        buffer = zlib.decompress(buffer, bufsize=uncompress_buffer_size)
    if zoom_level >= 0:
        count = data_tree_item.data_size // 32
        header = None
    else:
        header = read_wig_data_header(buffer)
        count = header.item_count
    min_loc_start = locs[locs_interval[0]].binned_start
    max_loc_end = locs[locs_interval[0]].binned_end
    for i in range(locs_interval[0] + 1, locs_interval[1]):
        if locs[i].binned_end > max_loc_end:
            max_loc_end = locs[i].binned_end
    while index < count:
        if zoom_level >= 0:  # zoom record
            record = read_zoom_data_record(buffer, index * 32)
            if record.valid_count == 0:
                index += 1
                continue
            data = DataInterval(
                record.chr_index,
                record.chr_start, record.chr_end,
                record.sum_data / record.valid_count)
        elif header.type == 1:  # bedgraph
            offset = 24 + index * 12
            start, end, value = struct.unpack("<IIf", buffer[offset:offset + 12])
            data = DataInterval(header.chr_index, start, end, value)
        elif header.type == 2:  # variable step wig
            offset = 24 + index * 8
            start, value = struct.unpack("<If", buffer[offset:offset + 8])
            data = DataInterval(header.chr_index, start, start + header.item_span, value)
        elif header.type == 3:  # fixed step wig
            offset = 24 + index * 4
            value = struct.unpack("<f", buffer[offset:offset + 4])[0]
            start = header.chr_start + index * header.item_step
            data = DataInterval(header.chr_index, start, start + header.item_span, value)
        else:
            raise RuntimeError(f"wig data type {header.type} invalid")
        index += 1
        if data.end <= min_loc_start:
            continue
        if data.start >= max_loc_end:
            break
        yield data


@dataclasses.dataclass
class BedEntry:
    chr_index: int
    start: int
    end: int
    fields: dict[str, str]


def iter_bed_entries(file, data_tree_item, locs, locs_interval, auto_sql, uncompress_buffer_size):
    offset = 0
    file.seek(data_tree_item.data_offset)
    buffer = file.read(data_tree_item.data_size)
    if uncompress_buffer_size > 0:
        buffer = zlib.decompress(buffer, bufsize=uncompress_buffer_size)
    first_loc = locs[locs_interval[0]]
    last_loc = locs[locs_interval[1] - 1]
    while offset < len(buffer):
        chr_index, start, end = struct.unpack("<III", buffer[offset:offset + 12])
        offset += 12
        end_offset = buffer.find(b'\0', offset)
        if end_offset == -1:
            raise RuntimeError("invalid bed entry (null terminator not found)")
        raw_fields = buffer[offset:end_offset].decode('utf-8')
        fields_list = raw_fields.split('\t') if raw_fields else []
        if len(fields_list) != len(auto_sql) - 3:
            raise RuntimeError("invalid bed entry (field count mismatch)")
        entry_fields = {}
        field_index = 0
        for sql_field_name in auto_sql.keys():
            if field_index >= 3:
                entry_fields[sql_field_name] = fields_list[field_index - 3]
            field_index += 1
        offset = end_offset + 1
        if end <= first_loc.binned_start:
            continue
        if start >= last_loc.binned_end:
            break
        yield BedEntry(chr_index, start, end, entry_fields)
