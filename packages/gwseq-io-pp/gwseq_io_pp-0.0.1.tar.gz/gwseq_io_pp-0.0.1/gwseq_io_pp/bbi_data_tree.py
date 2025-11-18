import collections
import dataclasses
import struct


@dataclasses.dataclass
class DataTreeNodeHeader:
    is_leaf: int
    # reserved: int
    count: int


def read_data_tree_node_header(file, offset):
    file.seek(offset)
    buffer = file.read(4)
    is_leaf = buffer[0]
    # reserved = buffer[1]
    count = struct.unpack("<H", buffer[2:4])[0]
    return DataTreeNodeHeader(is_leaf, count)


@dataclasses.dataclass
class DataTreeItem:
    start_chr_index: int
    start_base: int
    end_chr_index: int
    end_base: int
    data_offset: int
    data_size: int


@dataclasses.dataclass
class DataTreeGeneratorState:
    node_header: DataTreeNodeHeader
    node_buffer: bytes
    node_size: int
    item_index: int


def iter_data_tree(file, locs, locs_interval, offset):
    """Generator for traversing BigWig/BigBed R-tree data index."""
    locs_interval = list(locs_interval)  # Make mutable [start, end]
    def next_node(offset):
        """Read a node from the data tree."""
        node_header = read_data_tree_node_header(file, offset)
        node_size = 32 if node_header.is_leaf else 24
        file.seek(offset + 4)
        node_buffer = file.read(node_size * node_header.count)
        return DataTreeGeneratorState(node_header, node_buffer, node_size, 0)
    
    states = collections.deque([next_node(offset)])
    while states:
        state = states[0]
        if state.item_index == state.node_header.count:
            states.popleft()
            continue
        while state.item_index < state.node_header.count:
            item_buffer_offset = state.item_index * state.node_size

            # Read item coordinates
            item_start_chr_index, item_start_base, item_end_chr_index, item_end_base = \
            struct.unpack("<IIII", state.node_buffer[item_buffer_offset:item_buffer_offset + 16])
            
            # Find overlapping locations
            loc_index = locs_interval[0]
            while loc_index < locs_interval[1]:
                loc = locs[loc_index]
                
                # Skip locations before this item
                if (loc.chr_index < item_start_chr_index or 
                    (loc.chr_index == item_start_chr_index and 
                     loc.binned_end <= item_start_base and 
                     loc_index == locs_interval[0])):
                    locs_interval[0] += 1
                    loc_index += 1
                    continue
                
                # Stop if location is after this item
                if (loc.chr_index > item_end_chr_index or
                    (loc.chr_index == item_end_chr_index and 
                     loc.binned_start > item_end_base)):
                    break
                
                loc_index += 1
            
            # No overlapping locations found, move to next item
            if loc_index == locs_interval[0]:
                state.item_index += 1
                continue
            
            # Read data offset
            item_data_offset = struct.unpack("<Q", state.node_buffer[item_buffer_offset + 16:item_buffer_offset + 24])[0]
            
            if state.node_header.is_leaf:
                # Leaf node - yield the data item
                item_data_size = struct.unpack("<Q", state.node_buffer[item_buffer_offset + 24:item_buffer_offset + 32])[0]
                state.item_index += 1
                
                item = DataTreeItem(
                    item_start_chr_index,
                    item_start_base,
                    item_end_chr_index,
                    item_end_base,
                    item_data_offset,
                    item_data_size)
                yield item, (locs_interval[0], loc_index)
            else:
                # Internal node - traverse child
                state.item_index += 1
                states.appendleft(next_node(item_data_offset))
                break
