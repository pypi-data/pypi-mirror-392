import dataclasses


@dataclasses.dataclass
class ChrItem:
    id: str
    index: int
    size: int


@dataclasses.dataclass
class Loc:
    chr_index: int
    start: int
    end: int
    binned_start: int
    binned_end: int
    bin_size: float
    output_start_index: int
    output_end_index: int


def preparse_locs(chr_ids, starts=None, ends=None, centers=None, span=-1):
    preparsed_starts = []
    preparsed_ends = []
    if span >= 0:
        starts_specified = 0 if starts is None else 1
        ends_specified = 0 if ends is None else 1
        centers_specified = 0 if centers is None else 1
        if starts_specified + ends_specified + centers_specified != 1:
            raise ValueError("either starts/ends/centers must be specified when using span")
        elif starts_specified != 0:
            preparsed_starts = starts
            preparsed_ends = [s + span for s in starts]
        elif ends_specified != 0:
            preparsed_ends = ends
            preparsed_starts = [e - span for e in ends]
        else:
            preparsed_starts = [c - span // 2 for c in centers]
            preparsed_ends = [c + (span + 1) // 2 for c in centers]
    elif starts is None or ends is None:
        raise ValueError("either starts+ends or starts/ends/centers+span must be specified")
    else:
        preparsed_starts = starts
        preparsed_ends = ends
    if len(chr_ids) != len(preparsed_starts) or len(chr_ids) != len(preparsed_ends):
        raise ValueError("length mismatch between chr_ids and starts/ends/centers")
    return preparsed_starts, preparsed_ends


def parse_chr(chr_id, chr_map, key_size=-1):
    chr_key = chr_id
    if key_size >= 0:
        chr_key = chr_key[:key_size]
    if chr_key in chr_map:
        return chr_map[chr_key]
    chr_key_lower = chr_key.lower()
    if chr_key_lower in chr_map:
        return chr_map[chr_key_lower]
    chr_key_upper = chr_key.upper()
    if chr_key_upper in chr_map:
        return chr_map[chr_key_upper]
    if chr_id.lower().startswith("chr"):
        chr_key = chr_id[3:]
        if key_size >= 0:
            chr_key = chr_key[:key_size]
    else:
        chr_key = "chr" + chr_id
        if key_size >= 0:
            chr_key = chr_key[:key_size]
    if chr_key in chr_map:
        return chr_map[chr_key]
    chr_key_lower = chr_key.lower()
    if chr_key_lower in chr_map:
        return chr_map[chr_key_lower]
    chr_key_upper = chr_key.upper()
    if chr_key_upper in chr_map:
        return chr_map[chr_key_upper]
    available = ", ".join(chr_map.keys())
    raise RuntimeError(f"chromosome {chr_id} missing ({available})")


def parse_locs(chr_map, key_size, chr_ids, starts, ends, bin_size=1.0, bin_count=-1, full_bin=False):
    if len(chr_ids) != len(starts) or (len(ends) > 0 and len(chr_ids) != len(ends)):
        raise ValueError("length mismatch between chr_ids, starts or ends")
    locs = []
    binned_spans = set()
    for i in range(len(chr_ids)):
        loc = Loc(
            chr_index=parse_chr(chr_ids[i], chr_map, key_size).index,
            start=starts[i],
            end=ends[i],
            binned_start=0,
            binned_end=0,
            bin_size=0.0,
            output_start_index=0,
            output_end_index=0
        )
        if loc.start > loc.end:
            raise ValueError(f"loc {chr_ids[i]}:{loc.start}-{loc.end} at index {i} invalid")
        loc.binned_start = int((loc.start // bin_size) * bin_size)
        loc.binned_end = int((loc.end // bin_size + (1 if full_bin else 0)) * bin_size)
        locs.append(loc)
        binned_spans.add(loc.binned_end - loc.binned_start)
    if bin_count < 0:
        bin_count = int(max(binned_spans) // bin_size)
    locs.sort(key=lambda x: (x.chr_index, x.binned_start, x.binned_end))
    for i in range(len(chr_ids)):
        loc = locs[i]
        loc.bin_size = (loc.binned_end - loc.binned_start) / bin_count
        loc.output_start_index = i * bin_count
        loc.output_end_index = loc.output_start_index + bin_count
    return locs, bin_count


def get_locs_coverage(locs):
    coverage = 0
    for loc in locs:
        coverage += (loc.binned_end - loc.binned_start)
    return coverage
