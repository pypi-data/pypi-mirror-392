struct WigDataHeader {
    i64 chr_index;
    i64 chr_start;
    i64 chr_end;
    i64 item_step;
    i64 item_span;
    u8 type;
    // u8 reserved;
    i64 item_count;
};


struct ZoomDataRecord {
    i64 chr_index;
    i64 chr_start;
    i64 chr_end;
    i64 valid_count;
    f32 min_value;
    f32 max_value;
    f32 sum_data;
    f32 sum_squared;
};


WigDataHeader read_wig_data_header(const ByteArray& buffer) {
    WigDataHeader header;
    header.chr_index = static_cast<i64>(buffer.read<u32>(0));
    header.chr_start = static_cast<i64>(buffer.read<u32>(4));
    header.chr_end = static_cast<i64>(buffer.read<u32>(8));
    header.item_step = static_cast<i64>(buffer.read<u32>(12));
    header.item_span = static_cast<i64>(buffer.read<u32>(16));
    header.type = buffer.read<u8>(20);
    // header.reserved = buffer.read<u8>(21);
    header.item_count = buffer.read<u16>(22);
    return header;
}


ZoomDataRecord read_zoom_data_record(const ByteArray& buffer, i64 offset) {
    ZoomDataRecord record;
    record.chr_index = static_cast<i64>(buffer.read<u32>(offset));
    record.chr_start = static_cast<i64>(buffer.read<u32>(offset + 4));
    record.chr_end = static_cast<i64>(buffer.read<u32>(offset + 8));
    record.valid_count = static_cast<i64>(buffer.read<u32>(offset + 12));
    record.min_value = buffer.read<f32>(offset + 16);
    record.max_value = buffer.read<f32>(offset + 20);
    record.sum_data = buffer.read<f32>(offset + 24);
    record.sum_squared = buffer.read<f32>(offset + 28);
    return record;
}


struct DataInterval {
    i64 chr_index;
    i64 start;
    i64 end;
    f32 value;
};


class DataIntervalGenerator : public GeneratorBase<DataIntervalGenerator, DataInterval> {
    i64 min_loc_start;
    i64 max_loc_end;
    i64 zoom_level;
    ByteArray buffer;
    WigDataHeader header;
    i64 count;
    i64 index = 0;

public:
    DataIntervalGenerator(
        File& file,
        const DataTreeItem& data_tree_item,
        const std::vector<Loc>& locs,
        const LocsInterval& locs_interval,
        i64 zoom_level,
        i64 uncompress_buffer_size
    ) : zoom_level(zoom_level) {
        buffer = file.read(data_tree_item.data_size, data_tree_item.data_offset);
        if (uncompress_buffer_size > 0) buffer = buffer.decompressed(uncompress_buffer_size);
        if (zoom_level >= 0) {
            count = data_tree_item.data_size / 32;
        } else {
            header = read_wig_data_header(buffer);
            count = header.item_count;
        }
        min_loc_start = locs[locs_interval.start].binned_start;
        max_loc_end = locs[locs_interval.start].binned_end;
        for (i64 i = locs_interval.start + 1; i < locs_interval.end; ++i) {
            if (locs[i].binned_end > max_loc_end) max_loc_end = locs[i].binned_end;
        }
    }
    
    NextResult next() {
        while (index < count) {
            DataInterval data;
            if (zoom_level >= 0) { // zoom record
                ZoomDataRecord record = read_zoom_data_record(buffer, index * 32);
                if (record.valid_count == 0) {
                    index += 1;
                    continue;
                }
                data.chr_index = record.chr_index;
                data.start = record.chr_start;
                data.end = record.chr_end;
                data.value = record.sum_data / record.valid_count;
            } else if (header.type == 1) { // bedgraph
                data.chr_index = header.chr_index;
                data.start = static_cast<i64>(buffer.read<u32>(24 + index * 12));
                data.end = static_cast<i64>(buffer.read<u32>(24 + index * 12 + 4));
                data.value = buffer.read<f32>(24 + index * 12 + 8);
            } else if (header.type == 2) { // variable step wig
                data.chr_index = header.chr_index;
                data.start = static_cast<i64>(buffer.read<u32>(24 + index * 8));
                data.end = data.start + static_cast<i64>(header.item_span);
                data.value = buffer.read<f32>(24 + index * 8 + 4);
            } else if (header.type == 3) { // fixed step wig
                data.chr_index = header.chr_index;
                data.start = static_cast<i64>(header.chr_start) + index * header.item_step;
                data.end = data.start +  static_cast<i64>(header.item_span);
                data.value = buffer.read<f32>(24 + index * 4);
            } else {
                throw std::runtime_error(fstring("wig data type {} invalid", header.type));
            }
            index += 1;
            if (data.end <= min_loc_start) continue;
            if (data.start >= max_loc_end) break;
            return {data, false};
        }
        return {DataInterval{}, true};
    }
};


struct BedEntry {
    i64 chr_index;
    i64 start;
    i64 end;
    OrderedMap<str, str> fields;
};


class BedEntryGenerator : public GeneratorBase<BedEntryGenerator, BedEntry> {
    Loc first_loc;
    Loc last_loc;
    const OrderedMap<str, str>& auto_sql;
    ByteArray buffer;
    i64 offset = 0;

public:
    BedEntryGenerator(
        File& file,
        const DataTreeItem& data_tree_item,
        const std::vector<Loc>& locs,
        const LocsInterval& locs_interval,
        const OrderedMap<str, str>& auto_sql,
        i64 uncompress_buffer_size
    ) : auto_sql(auto_sql) {
        buffer = file.read(data_tree_item.data_size, data_tree_item.data_offset);
        if (uncompress_buffer_size > 0) buffer = buffer.decompressed(uncompress_buffer_size);
        first_loc = locs[locs_interval.start];
        last_loc = locs[locs_interval.end - 1];
    }

    NextResult next() {
        while (offset < buffer.size()) {
            BedEntry entry;
            entry.chr_index = buffer.read<u32>(offset);
            entry.start = buffer.read<u32>(offset + 4);
            entry.end = buffer.read<u32>(offset + 8);
            offset += 12;
            i64 end_offset = buffer.find('\0', offset);
            if (end_offset == -1) throw std::runtime_error("invalid bed entry (null terminator not found)");
            str raw_fields = buffer.read_string(offset, end_offset - offset);
            auto fields = split_string(raw_fields, '\t');
            if (static_cast<i64>(fields.size()) != auto_sql.size() - 3) {
                throw std::runtime_error("invalid bed entry (field count mismatch)");
            }
            i64 field_index = 0;
            for (const auto& sql_field : auto_sql) {
                if (field_index >= 3) {
                    entry.fields.insert(sql_field.first, fields[field_index - 3]);
                }
                field_index += 1;
            }
            offset = end_offset + 1;
            if (entry.end <= first_loc.binned_start) continue;
            if (entry.start >= last_loc.binned_end) break;
            return {entry, false};
        }
        return {BedEntry{}, true};
    }
};
