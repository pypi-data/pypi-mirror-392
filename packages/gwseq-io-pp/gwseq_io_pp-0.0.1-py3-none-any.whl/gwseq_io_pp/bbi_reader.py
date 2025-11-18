import struct
import numpy as np

from .bbi_headers import read_bbi_header, read_zoom_headers, read_auto_sql, \
    read_total_summary, read_chr_tree_header, read_chr_list, BIGWIG_MAGIC
from .bbi_locs import preparse_locs, parse_locs
from .bbi_data_tree import iter_data_tree
from .bbi_data_values import iter_data_intervals, iter_bed_entries


class BBIReader:
    def __init__(self, path, zoom_correction=1/3):
        self.path = path
        self.file = open(path, "rb")
        self.zoom_correction = zoom_correction
        self.bbi_header = read_bbi_header(self.file)
        self.zoom_headers = read_zoom_headers(self.file, self.bbi_header.zoom_levels)
        self.auto_sql = read_auto_sql(self.file, self.bbi_header.auto_sql_offset, self.bbi_header.field_count)
        self.total_summary = read_total_summary(self.file, self.bbi_header.total_summary_offset)
        self.chr_tree_header = read_chr_tree_header(self.file, self.bbi_header.chr_tree_offset)
        self.chr_list = read_chr_list(self.file, self.bbi_header.chr_tree_offset + 32, self.chr_tree_header.key_size)
        self.chr_map = {item.id: item for item in self.chr_list}
        self.type = "bigwig" if self.bbi_header.magic == BIGWIG_MAGIC else "bigbed"
        self.file.seek(self.bbi_header.full_data_offset)
        self.data_count = struct.unpack("<I", self.file.read(4))[0]

    def __close__(self):
        self.close()

    def close(self):
        self.file.close()

    def select_zoom_level(self, bin_size, request=-1):
        zoom_count = len(self.zoom_headers)
        if request >= -1:
            if request < zoom_count:
                return request
            raise RuntimeError(f"requested zoom level {request} exceeds max zoom level {zoom_count - 1}")
        best_level = -1
        best_reduction = 0
        rounded_bin_size = round(bin_size * self.zoom_correction)
        for i in range(zoom_count):
            reduction = self.zoom_headers[i].reduction_level
            if reduction <= rounded_bin_size and reduction > best_reduction:
                best_reduction = reduction
                best_level = i
        return best_level

    def init_extraction(self, chr_ids, starts=None, ends=None, centers=None, span=-1, bin_size=1.0, bin_count=-1, full_bin=False, zoom=-1):
        preparsed_starts, preparsed_ends = preparse_locs(chr_ids, starts, ends, centers, span)
        locs, bin_count = parse_locs(self.chr_map, self.chr_tree_header.key_size, chr_ids, preparsed_starts, preparsed_ends, bin_size, bin_count, full_bin)
        zoom_level = self.select_zoom_level(bin_size, zoom)
        data_tree_offset = self.bbi_header.full_index_offset + 48 if zoom_level < 0 else self.zoom_headers[zoom_level].index_offset + 48
        return locs, bin_count, zoom_level, data_tree_offset

    def entries_pileup(self, locs, zoom_level, data_tree_offset):
        locs_interval = (0, len(locs))
        output_size = 0 if not locs else locs[-1].output_end_index
        output = np.zeros(output_size, dtype=np.float32)
        for tree_item, item_locs_interval in iter_data_tree(self.file, locs, locs_interval, data_tree_offset):
            for entry in iter_bed_entries(self.file, tree_item, locs, item_locs_interval, self.auto_sql, self.bbi_header.uncompress_buffer_size):
                for loc_index in range(item_locs_interval[0], item_locs_interval[1]):
                    loc = locs[loc_index]
                    if entry.chr_index != loc.chr_index:
                        continue
                    if entry.start >= loc.binned_end:
                        continue
                    if entry.end <= loc.binned_start:
                        break
                    overlap_start = max(entry.start, loc.binned_start)
                    overlap_end = min(entry.end, loc.binned_end)
                    loc_bin_start = int(loc.binned_start // loc.bin_size)
                    bin_start = int(overlap_start // loc.bin_size)
                    bin_end = int(-(-overlap_end // loc.bin_size)) # ceiling division
                    for b in range(bin_start, bin_end):
                        output_index = loc.output_start_index + (b - loc_bin_start)
                        if output_index >= loc.output_end_index:
                            break
                        output[output_index] += 1.0
        return output
    
    def reduce_output_stats(self, output_stats, reduce, def_value):
        output = np.full(len(output_stats), def_value, dtype=np.float32)
        # output_stats columns: [min, max, sum, sum_squared, count]
        mask = output_stats[:, 4] > 0  # count > 0
        if reduce == "mean":
            output[mask] = output_stats[mask, 2] / output_stats[mask, 4]
        elif reduce == "sd":
            means = output_stats[mask, 2] / output_stats[mask, 4]
            variances = (output_stats[mask, 3] / output_stats[mask, 4]) - (means * means)
            output[mask] = np.sqrt(variances)
        elif reduce == "sem":
            means = output_stats[mask, 2] / output_stats[mask, 4]
            variances = (output_stats[mask, 3] / output_stats[mask, 4]) - (means * means)
            output[mask] = np.sqrt(variances) / np.sqrt(output_stats[mask, 4])
        elif reduce == "sum":
            output[mask] = output_stats[mask, 2]
        elif reduce == "count":
            output[mask] = output_stats[mask, 4]
        elif reduce == "min":
            output[mask] = output_stats[mask, 0]
        elif reduce == "max":
            output[mask] = output_stats[mask, 1]
        else:
            raise RuntimeError(f"reduce {reduce} not recognized")
        return output

    def read_signal(self, chr_ids, starts=None, ends=None, centers=None, span=-1, bin_size=1.0, bin_count=-1, bin_mode="mean", full_bin=False, def_value=0.0, zoom=-1):
        locs, _, zoom_level, data_tree_offset = self.init_extraction(chr_ids, starts, ends, centers, span, bin_size, bin_count, full_bin, zoom)
        if self.type == "bigbed":
            output = self.entries_pileup(locs, zoom_level, data_tree_offset)
        else:
            locs_interval = (0, len(locs))
            output_size = 0 if not locs else locs[-1].output_end_index
            output_stats = np.zeros((output_size, 2), dtype=np.float32) # 2 for sum, count
            for tree_item, item_locs_interval in iter_data_tree(self.file, locs, locs_interval, data_tree_offset):
                for interval in iter_data_intervals(self.file, tree_item, locs, item_locs_interval, zoom_level, self.bbi_header.uncompress_buffer_size):
                    for loc_index in range(item_locs_interval[0], item_locs_interval[1]):
                        loc = locs[loc_index]
                        if interval.start >= loc.binned_end:
                            continue
                        if interval.end <= loc.binned_start:
                            break
                        overlap_start = max(interval.start, loc.binned_start)
                        overlap_end = min(interval.end, loc.binned_end)
                        loc_bin_start = int(loc.binned_start // loc.bin_size)
                        bin_start = int(overlap_start // loc.bin_size)
                        bin_end = int(-(-overlap_end // loc.bin_size)) # ceiling division
                        for b in range(bin_start, bin_end):
                            output_index = loc.output_start_index + (b - loc_bin_start)
                            if output_index >= loc.output_end_index:
                                break
                            value_stats = output_stats[output_index]
                            value_stats[0] += interval.value # sum
                            value_stats[1] += 1 # count
            sum_values = output_stats[:, 0]
            counts = output_stats[:, 1]
            mask = counts > 0
            output = np.full(output_size, def_value, dtype=np.float32)
            if bin_mode == "mean":
                output[mask] = sum_values[mask] / counts[mask]
            elif bin_mode == "sum":
                output[mask] = sum_values[mask]
            elif bin_mode == "count":
                output[mask] = counts[mask]
            else:
                raise RuntimeError(f"bin_mode {bin_mode} not recognized")
        output = output.reshape((len(locs), -1))
        return output
    
    def quantify(self, chr_ids, starts=None, ends=None, centers=None, span=-1, bin_size=1.0, full_bin=False, def_value=0.0, reduce="mean", zoom=-1):
        locs, _, zoom_level, data_tree_offset = self.init_extraction(chr_ids, starts, ends, centers, span, bin_size, bin_count=1, full_bin=full_bin, zoom=zoom)
        locs_interval = (0, len(locs))
        output_stats = np.zeros((len(locs), 5), dtype=np.float32) # 5 for min, max, sum, sum_squared, count
        if self.type == "bigbed":
            pileup = self.entries_pileup(locs, zoom_level, data_tree_offset)
            pileup = pileup.reshape((len(locs), -1))
            output_stats[:, 0] = np.min(pileup, axis=1) # min
            output_stats[:, 1] = np.max(pileup, axis=1) # max
            output_stats[:, 2] = np.sum(pileup, axis=1) # sum
            output_stats[:, 3] = np.sum(pileup * pileup, axis=1) # sum_squared
            output_stats[:, 4] = np.sum(pileup > 0, axis=1) # count
        else:
            for tree_item, item_locs_interval in iter_data_tree(self.file, locs, locs_interval, data_tree_offset):
                for interval in iter_data_intervals(self.file, tree_item, locs, item_locs_interval, zoom_level, self.bbi_header.uncompress_buffer_size):
                    for loc_index in range(item_locs_interval[0], item_locs_interval[1]):
                        loc = locs[loc_index]
                        if interval.start >= loc.binned_end:
                            continue
                        if interval.end <= loc.binned_start:
                            break
                        overlap_start = max(interval.start, loc.binned_start)
                        overlap_end = min(interval.end, loc.binned_end)
                        overlap = overlap_end - overlap_start
                        value_stats = output_stats[loc_index]
                        if interval.value < value_stats[0] or np.isnan(value_stats[0]):
                            value_stats[0] = interval.value # min
                        if interval.value > value_stats[1] or np.isnan(value_stats[1]):
                            value_stats[1] = interval.value # max
                        value_stats[2] += interval.value * overlap # sum
                        value_stats[3] += interval.value * interval.value * overlap # sum_squared
                        value_stats[4] += overlap # count
        return self.reduce_output_stats(output_stats, reduce, def_value)

    def profile(self, chr_ids, starts=None, ends=None, centers=None, span=-1, bin_size=1.0, bin_count=-1, bin_mode="mean", full_bin=False, def_value=0.0, reduce="mean", zoom=-1):
        locs, bin_count, zoom_level, data_tree_offset = self.init_extraction(chr_ids, starts, ends, centers, span, bin_size, bin_count, full_bin, zoom)
        locs_interval = (0, len(locs))
        output_stats = np.zeros((bin_count, 5), dtype=np.float32) # 5 for min, max, sum, sum_squared, count
        if self.type == "bigbed":
            pileup = self.entries_pileup(locs, zoom_level, data_tree_offset)
            pileup = pileup.reshape((len(locs), -1))
            output_stats[:, 0] = np.min(pileup, axis=0) # min
            output_stats[:, 1] = np.max(pileup, axis=0) # max
            output_stats[:, 2] = np.sum(pileup, axis=0) # sum
            output_stats[:, 3] = np.sum(pileup * pileup, axis=0) # sum_squared
            output_stats[:, 4] = np.sum(pileup > 0, axis=0) # count
        else:
            for tree_item, item_locs_interval in iter_data_tree(self.file, locs, locs_interval, data_tree_offset):
                for interval in iter_data_intervals(self.file, tree_item, locs, item_locs_interval, zoom_level, self.bbi_header.uncompress_buffer_size):
                    for loc_index in range(item_locs_interval[0], item_locs_interval[1]):
                        loc = locs[loc_index]
                        if interval.start >= loc.binned_end:
                            continue
                        if interval.end <= loc.binned_start:
                            break
                        overlap_start = max(interval.start, loc.binned_start)
                        overlap_end = min(interval.end, loc.binned_end)
                        loc_bin_start = int(loc.binned_start // loc.bin_size)
                        bin_start = int(overlap_start // loc.bin_size)
                        bin_end = int(-(-overlap_end // loc.bin_size)) # ceiling division
                        for b in range(bin_start, bin_end):
                            output_index = b - loc_bin_start
                            if output_index >= bin_count:
                                break
                            value_stats = output_stats[output_index]
                            if interval.value < value_stats[0] or np.isnan(value_stats[0]):
                                value_stats[0] = interval.value # min
                            if interval.value > value_stats[1] or np.isnan(value_stats[1]):
                                value_stats[1] = interval.value # max
                            value_stats[2] += interval.value # sum
                            value_stats[3] += interval.value * interval.value # sum_squared
                            value_stats[4] += 1 # count
        return self.reduce_output_stats(output_stats, reduce, def_value)

    def read_entries(self, chr_ids, starts=None, ends=None, centers=None, span=-1, bin_size=1.0, full_bin=False):
        if self.type != "bigbed":
            raise RuntimeError("read_entries only for bigbed")
        locs, _, _, data_tree_offset = self.init_extraction(chr_ids, starts, ends, centers, span, bin_size, bin_count=1, full_bin=full_bin, zoom=-1)
        output = [[] for _ in locs]
        locs_interval = (0, len(locs))
        for tree_item, item_locs_interval in iter_data_tree(self.file, locs, locs_interval, data_tree_offset):
            for entry in iter_bed_entries(self.file, tree_item, locs, item_locs_interval, self.auto_sql, self.bbi_header.uncompress_buffer_size):
                for loc_index in range(item_locs_interval[0], item_locs_interval[1]):
                    loc = locs[loc_index]
                    if entry.chr_index != loc.chr_index:
                        continue
                    if entry.start >= loc.binned_end:
                        continue
                    if entry.end <= loc.binned_start:
                        break
                    output[loc_index].append(entry)
        return output
