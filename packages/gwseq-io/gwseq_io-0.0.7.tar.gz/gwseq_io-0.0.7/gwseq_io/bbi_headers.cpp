const u32 BIGWIG_MAGIC = 0x888FFC26;
const u32 BIGBED_MAGIC = 0x8789F2EB;
const u32 BIGWIG_MAGIC_SWAPPED = 0x26FC8F88;
const u32 BIGBED_MAGIC_SWAPPED = 0xEBF28987;

const u32 CHR_TREE_MAGIC = 0x78CA8C91;
const u32 CHR_TREE_MAGIC_SWAPPED = 0x91CA8C78;

const u16 BBI_MIN_VERSION = 3;
const u16 BBI_OUTPUT_VERSION = 4;


struct BBIHeader {
    u32 magic;
    u16 version;
    i64 zoom_levels;
    i64 chr_tree_offset;
    i64 full_data_offset;
    i64 full_index_offset;
    i64 field_count;
    i64 defined_field_count;
    i64 auto_sql_offset;
    i64 total_summary_offset;
    i64 uncompress_buffer_size;
    // u64 reserved;
};


struct ZoomHeader {
    i64 reduction_level;
    // u32 reserved;
    i64 data_offset;
    i64 index_offset;
};


struct TotalSummary {
    i64 bases_covered;
    f64 min_value;
    f64 max_value;
    f64 sum_data;
    f64 sum_squared;
};


struct ChrTreeHeader {
    u32 magic;
    i64 block_size;
    i64 key_size;
    i64 value_size;
    i64 item_count;
    // u64 reserved;
};


struct DataTreeHeader {
    u32 magic;
    i64 block_size;
    i64 item_count;
    i64 start_chr_index;
    i64 start_base;
    i64 end_chr_index;
    i64 end_base;
    i64 end_file_offset;
    i64 items_per_slot;
    // u8 reserved;
};


BBIHeader read_bbi_header(File& file) {
    ByteArray buffer = file.read(64, 0);
    BBIHeader header;
    header.magic = buffer.read<u32>(0);
    if (header.magic != BIGWIG_MAGIC && header.magic != BIGBED_MAGIC) {
        if (header.magic == BIGWIG_MAGIC_SWAPPED || header.magic == BIGBED_MAGIC_SWAPPED) {
            throw std::runtime_error("incompatible endianness");
        }
        throw std::runtime_error("not a bigwig or bigbed file");
    }
    header.version = buffer.read<u16>(4);
    if (header.version < BBI_MIN_VERSION) {
        throw std::runtime_error(
            "bigwig or bigbed version " + std::to_string(header.version) +
            " unsupported (>= " + std::to_string(BBI_MIN_VERSION) + ")"
        );
    }
    header.zoom_levels = static_cast<i64>(buffer.read<u16>(6));
    header.chr_tree_offset = static_cast<i64>(buffer.read<u64>(8));
    header.full_data_offset = static_cast<i64>(buffer.read<u64>(16));
    header.full_index_offset = static_cast<i64>(buffer.read<u64>(24));
    header.field_count = static_cast<i64>(buffer.read<u16>(32));
    header.defined_field_count = static_cast<i64>(buffer.read<u16>(34));
    header.auto_sql_offset = static_cast<i64>(buffer.read<u64>(36));
    header.total_summary_offset = static_cast<i64>(buffer.read<u64>(44));
    header.uncompress_buffer_size = static_cast<i64>(buffer.read<u32>(52));
    // header.reserved = buffer.read<u64>(56);
    return header;
}


std::vector<ZoomHeader> read_zoom_headers(File& file, i64 zoom_levels) {
    std::vector<ZoomHeader> headers;
    if (zoom_levels == 0) return headers;
    ByteArray buffer = file.read(zoom_levels * 24, 64);
    for (i64 i = 0; i < zoom_levels; ++i) {
        ZoomHeader header;
        header.reduction_level = static_cast<i64>(buffer.read<u32>(i * 24));
        // header.reserved = buffer.read<u32>(i * 24 + 4);
        header.data_offset = static_cast<i64>(buffer.read<u64>(i * 24 + 8));
        header.index_offset = static_cast<i64>(buffer.read<u64>(i * 24 + 16));
        headers.push_back(header);
    }
    return headers;
}


OrderedMap<str, str> read_auto_sql(File& file, i64 offset, i64 field_count) {
    if (offset == 0) return {};
    str sql_string = file.read_until('\0', offset).to_string(false);
    OrderedMap<str, str> fields;
    std::regex re(R"(\s*(\S+)\s+([^;]+);)");
    std::smatch match;
    std::istringstream iss(sql_string);
    str line;
    while (std::getline(iss, line)) {
        if (std::regex_search(line, match, re)) {
            str type = match[1];
            str field_list = match[2];
            std::regex field_re(R"(\s*(\S+)\s*(?:,|$))");
            std::sregex_iterator iter(field_list.begin(), field_list.end(), field_re);
            std::sregex_iterator end;
            for (; iter != end; ++iter) {
                str name = (*iter)[1].str();
                if (!name.empty()) {
                    fields.insert(name, type);
                }
            }
        }
    }
    if (fields.size() < 3
    || !std::regex_match(fields.key_at_index(0), std::regex(R"(^chr(?:om)_?(?:id|name)?$)", std::regex_constants::icase))
    || !std::regex_match(fields.key_at_index(1), std::regex(R"(^(?:chr(?:om)?_?)?start$)", std::regex_constants::icase))
    || !std::regex_match(fields.key_at_index(2), std::regex(R"(^(?:chr(?:om)?_?)?end$)", std::regex_constants::icase))) {
        throw std::runtime_error("missing or misplaced chr, start or end in autosql");
    }
    if (fields.size() != field_count) {
        throw std::runtime_error(fstring("field count {} does not match autosql field count {}", field_count, fields.size()));
    }
    return fields;
}


TotalSummary read_total_summary(File& file, i64 offset) {
    ByteArray buffer = file.read(40, offset);
    TotalSummary summary;
    summary.bases_covered = static_cast<i64>(buffer.read<u64>(0));
    summary.min_value = buffer.read<f64>(8);
    summary.max_value = buffer.read<f64>(16);
    summary.sum_data = buffer.read<f64>(24);
    summary.sum_squared = buffer.read<f64>(32);
    return summary;
}


ChrTreeHeader read_chr_tree_header(File& file, i64 offset) {
    ByteArray buffer = file.read(32, offset);
    ChrTreeHeader header;
    header.magic = buffer.read<u32>(0);
    if (header.magic != CHR_TREE_MAGIC) {
        if (header.magic == CHR_TREE_MAGIC_SWAPPED) {
            throw std::runtime_error("incompatible endianness (chromosome tree)");
        }
        throw std::runtime_error("invalid chr tree magic number");
    }
    header.block_size = static_cast<i64>(buffer.read<u32>(4));
    header.key_size = static_cast<i64>(buffer.read<u32>(8));
    header.value_size = static_cast<i64>(buffer.read<u32>(12));
    header.item_count = static_cast<i64>(buffer.read<u64>(16));
    // header.reserved = buffer.read<u64>(24);
    return header;
}


std::vector<ChrItem> read_chr_list(File& file, i64 offset, i64 key_size) {
    std::vector<ChrItem> items;
    ByteArray header_buffer = file.read(4, offset);
    u8 is_leaf = header_buffer.read<u8>(0);
    // u8 reserved = header_buffer.read<u8>(1);
    i64 count = static_cast<i64>(header_buffer.read<u16>(2));
    ByteArray buffer = file.read(count * (key_size + 8), offset + 4);
    for (i64 i = 0; i < count; i += 1) {
        i64 buffer_index = i * (key_size + 8);
        if (is_leaf) {
            ChrItem item;
            item.id = buffer.read_string(buffer_index, key_size);
            item.index = static_cast<i64>(buffer.read<u32>(buffer_index + key_size));
            item.size = static_cast<i64>(buffer.read<u32>(buffer_index + key_size + 4));
            items.push_back(item);
        } else {
            // str key = buffer.read_string(buffer_index, key_size);
            u64 child_offset = buffer.read<u64>(buffer_index + key_size);
            auto child_items = read_chr_list(file, child_offset, key_size);
            items.insert(items.end(), child_items.begin(), child_items.end());
        }
    }
    std::sort(items.begin(), items.end(), [](const ChrItem& a, const ChrItem& b) {
        return a.index < b.index;
    });
    return items;
}
