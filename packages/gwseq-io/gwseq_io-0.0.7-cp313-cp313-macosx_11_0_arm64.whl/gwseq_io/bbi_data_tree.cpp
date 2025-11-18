struct DataTreeNodeHeader {
    u8 is_leaf;
    // u8 reserved;
    i64 count;
};


DataTreeNodeHeader read_data_tree_node_header(File& file, i64 offset) {
    ByteArray buffer = file.read(4, offset);
    DataTreeNodeHeader node_header;
    node_header.is_leaf = buffer.read<u8>(0);
    // node_header.reserved = buffer.read<u8>(1);
    node_header.count = static_cast<i64>(buffer.read<u16>(2));
    return node_header;
}


struct DataTreeItem {
    i64 start_chr_index;
    i64 start_base;
    i64 end_chr_index;
    i64 end_base;
    i64 data_offset;
    i64 data_size;
};


struct DataTreeGeneratorItem {
    DataTreeItem item;
    LocsInterval locs;
};

struct DataTreeGeneratorState {
    DataTreeNodeHeader node_header;
    ByteArray node_buffer;
    i64 node_size;
    i64 item_index;
};


class DataTreeGenerator : public GeneratorBase<DataTreeGenerator, DataTreeGeneratorItem> {
    File& file;
    const std::vector<Loc>& locs;
    LocsInterval locs_interval;
    ProgressTracker& tracker;
    std::deque<DataTreeGeneratorState> states;

    DataTreeGeneratorState next_node(i64 offset) {
        auto node_header = read_data_tree_node_header(file, offset);
        i64 node_size = node_header.is_leaf ? 32 : 24;
        ByteArray node_buffer = file.read(node_size * node_header.count, offset + 4);
        return {node_header, node_buffer, node_size, 0};
    }

public:
    DataTreeGenerator(
        File& file,
        const std::vector<Loc>& locs,
        LocsInterval locs_interval,
        ProgressTracker& tracker,
        i64 offset
    ) : file(file), locs(locs), locs_interval(locs_interval), tracker(tracker) {
            states.push_front(next_node(offset));
        }

    NextResult next() {
        while (!states.empty()) {
            DataTreeGeneratorState& state = states.front();
            if (state.item_index == state.node_header.count) {
                states.pop_front();
                continue;
            }
            while (state.item_index < state.node_header.count) {
                i64 item_buffer_offset = state.item_index * state.node_size;
                i64 item_start_chr_index = static_cast<i64>(state.node_buffer.read<u32>(item_buffer_offset));
                i64 item_start_base = static_cast<i64>(state.node_buffer.read<u32>(item_buffer_offset + 4));
                i64 item_end_chr_index = static_cast<i64>(state.node_buffer.read<u32>(item_buffer_offset + 8));
                i64 item_end_base = static_cast<i64>(state.node_buffer.read<u32>(item_buffer_offset + 12));
                i64 loc_index = locs_interval.start;
                while (loc_index < locs_interval.end) {
                    auto loc = locs[loc_index];
                    if (loc.chr_index < item_start_chr_index
                    || (loc.chr_index == item_start_chr_index && loc.binned_end <= item_start_base && loc_index == locs_interval.start)) {
                        tracker.add(loc.binned_end - loc.binned_start);
                        locs_interval.start += 1;
                        loc_index += 1;
                        continue;
                    }
                    if (loc.chr_index > item_end_chr_index
                    || (loc.chr_index == item_end_chr_index && loc.binned_start > item_end_base)) {
                        break;
                    }
                    loc_index += 1;
                }
                if (loc_index == locs_interval.start) {
                    state.item_index += 1;
                    continue;
                }
                i64 item_data_offset = static_cast<i64>(state.node_buffer.read<u64>(item_buffer_offset + 16));
                if (state.node_header.is_leaf) {
                    i64 item_data_size = static_cast<i64>(state.node_buffer.read<u64>(item_buffer_offset + 24));
                    state.item_index += 1;
                    return {{{item_start_chr_index, item_start_base, item_end_chr_index, item_end_base, item_data_offset, item_data_size}, {locs_interval.start, loc_index}}, false};
                } else {
                    state.item_index += 1;
                    states.push_front(next_node(item_data_offset));
                    break;
                }
            }
        }
        while (locs_interval.start < locs_interval.end) {
            auto loc = locs[locs_interval.start];
            tracker.add(loc.binned_end - loc.binned_start);
            locs_interval.start += 1;
        }
        return {{{}, {}}, true};
    }
};
