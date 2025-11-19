struct HiCHeader {
    i64 version;
    i64 footer_position;
    str genome_id;
    i64 nvi_position;
    i64 nvi_length;
    OrderedMap<str, str> attributes;
    OrderedMap<str, ChrItem> chr_map;
    std::vector<i64> bp_resolutions;
    std::vector<i64> frag_resolutions;
    std::vector<i64> sites;
};


struct HiCIndexItem {
    i64 position;
    i64 size;
};


struct ExpectedValueVector {
    str normalization;
    str unit;
    i64 bin_size;
    std::vector<f32> values;
    OrderedMap<i64, f32> chr_scale_factors;
};


struct NormalizationVector {
    str normalization;
    i64 chr_index;
    str unit;
    i64 bin_size;
    i64 position;
    i64 byte_count;
};


struct HiCFooter {
    i64 byte_count_v5;
    OrderedMap<str, str> attributes;
    OrderedMap<str, HiCIndexItem> master_index;
    OrderedMap<str, ExpectedValueVector> expected_value_vectors;
    OrderedMap<str, NormalizationVector> normalization_vectors;  
    std::set<str> normalizations;
    std::set<str> units;
};


str get_vector_key(
    const str& normalization,
    i64 bin_size,
    const str& unit,
    i64 chr_index = -1
) {
    str key = 
        "normalization=" + normalization + "|" +
        "bin_size=" + std::to_string(bin_size) + "|" +
        "unit=" + unit;
    if (chr_index != -1) key = "chr_index=" + std::to_string(chr_index) + "|" + key;
    return key;
}


HiCHeader read_hic_header(File& file) {
    ByteStream stream = file.to_stream();
    HiCHeader header;
    str magic = stream.read_string(4);
    if (magic != "HIC") throw std::runtime_error("not a hic file (magic: '" + magic + "')");
    header.version = static_cast<i64>(stream.read<i32>());
    if (header.version < 6) throw std::runtime_error(
        "hic version " + std::to_string(header.version) +
        " unsupported (>= 6)"
    );
    header.footer_position = stream.read<i64>();
    header.genome_id = stream.read_until('\0').to_string();
    if (header.version > 8) {
        header.nvi_position = stream.read<i64>();
        header.nvi_length = stream.read<i64>();
    }
    i32 attribute_count = stream.read<i32>();
    for (i32 i = 0; i < attribute_count; ++i) {
        str key = stream.read_until('\0').to_string();
        str value = stream.read_until('\0').to_string();
        header.attributes.insert(key, value);
    }
    i32 chr_count = stream.read<i32>();
    for (i32 i = 0; i < chr_count; ++i) {
        ChrItem chr_item;
        chr_item.id = stream.read_until('\0').to_string();
        chr_item.index = static_cast<i64>(i);
        if (header.version > 8) {
            chr_item.size = stream.read<i64>();
        } else {
            chr_item.size = static_cast<i64>(stream.read<i32>());
        }
        header.chr_map.insert(chr_item.id, chr_item);
    }
    i32 bp_resolution_count = stream.read<i32>();
    header.bp_resolutions.reserve(bp_resolution_count);
    for (i32 i = 0; i < bp_resolution_count; ++i) {
        header.bp_resolutions.push_back(static_cast<i64>(stream.read<i32>()));
    }
    i32 frag_resolution_count = stream.read<i32>();
    header.frag_resolutions.reserve(frag_resolution_count);
    for (i32 i = 0; i < frag_resolution_count; ++i) {
        header.frag_resolutions.push_back(static_cast<i64>(stream.read<i32>()));
    }
    i32 site_count = stream.read<i32>();
    header.sites.reserve(site_count);
    for (i32 i = 0; i < site_count; ++i) {
        header.sites.push_back(static_cast<i64>(stream.read<i32>()));
    }
    return header;
}


HiCFooter read_hic_footer(
    File& file,
    i64 version,
    i64 footer_position
) {
    ByteStream stream = file.to_stream(footer_position);
    HiCFooter footer;
    if (version > 8) {
        footer.byte_count_v5 = stream.read<i64>();
    } else {
        footer.byte_count_v5 = static_cast<i64>(stream.read<i32>());
    }
    i32 master_index_count = stream.read<i32>();
    for (i32 i = 0; i < master_index_count; ++i) {
        HiCIndexItem item;
        str key = stream.read_until('\0').to_string();
        item.position = stream.read<i64>();
        item.size = static_cast<i64>(stream.read<i32>());
        footer.master_index.insert(key, item);
    }
    for (auto is_normalized : {false, true}) {
        i32 expected_value_vector_count = stream.read<i32>();
        for (i32 i = 0; i < expected_value_vector_count; ++i) {
            ExpectedValueVector vector;
            vector.normalization = is_normalized
                ? to_lowercase(stream.read_until('\0').to_string())
                : "none";
            footer.normalizations.insert(vector.normalization);
            vector.unit = to_lowercase(stream.read_until('\0').to_string());
            footer.units.insert(vector.unit);
            vector.bin_size = static_cast<i64>(stream.read<i32>());
            if (version > 8) {
                i64 value_count = stream.read<i64>();
                vector.values = stream.read_array<f32>(value_count);
            } else {
                i32 value_count = stream.read<i32>();
                std::vector<f64> values = stream.read_array<f64>(value_count);
                vector.values = std::vector<f32>(values.begin(), values.end());
            }
            i32 chr_scale_factor_count = stream.read<i32>();
            for (i32 j = 0; j < chr_scale_factor_count; ++j) {
                i64 chr_index = static_cast<i64>(stream.read<i32>());
                f32 scale_factor = (version > 8)
                    ? stream.read<f32>()
                    : static_cast<f32>(stream.read<f64>());
                vector.chr_scale_factors.insert(chr_index, scale_factor);
            }
            auto key = get_vector_key(vector.normalization, vector.bin_size, vector.unit);
            footer.expected_value_vectors.insert(key, vector);
        }
    }
    i32 normalization_vector_count = stream.read<i32>();
    for (i32 i = 0; i < normalization_vector_count; ++i) {
        NormalizationVector vector;
        vector.normalization = to_lowercase(stream.read_until('\0').to_string());
        footer.normalizations.insert(vector.normalization);
        vector.chr_index = static_cast<i64>(stream.read<i32>());
        vector.unit = to_lowercase(stream.read_until('\0').to_string());
        footer.units.insert(vector.unit);
        vector.bin_size = static_cast<i64>(stream.read<i32>());
        vector.position = stream.read<i64>();
        vector.byte_count = (version > 8)
            ? stream.read<i64>()
            : static_cast<i64>(stream.read<i32>());
        auto key = get_vector_key(vector.normalization, vector.bin_size, vector.unit, vector.chr_index);
        footer.normalization_vectors.insert(key, vector);
    }
    return footer;
}


std::vector<f32> compute_expected_values(
    const OrderedMap<str, ExpectedValueVector>& expected_value_vectors,
    const str& normalization,
    i64 bin_size,
    const str& unit,
    i64 chr_index
) {
    auto key = get_vector_key(normalization, bin_size, unit);
    auto it_vector = expected_value_vectors.find(key);
    if (it_vector == expected_value_vectors.end()) {
        throw std::runtime_error("expected value vector " + key + " not found");
    }
    const ExpectedValueVector& vector = it_vector->second;
    auto it_factor = vector.chr_scale_factors.find(chr_index);
    if (it_factor == vector.chr_scale_factors.end()) {
        key = get_vector_key(normalization, bin_size, unit, chr_index);
        throw std::runtime_error("expected value vector " + key + " not found");
    }
    f32 scale_factor = 1.0f / it_factor->second;
    std::vector<f32> expected_values;
    expected_values.reserve(vector.values.size());
    for (f32 value : vector.values) {
        expected_values.push_back(value * scale_factor);
    }
    return expected_values;
}


std::vector<f32> get_normalization_vector_from_file(
    File& file,
    i64 version,
    const OrderedMap<str, NormalizationVector>& normalization_vectors,
    i64 chr_index,
    const str& normalization,
    i64 bin_size,
    const str& unit
) {
    auto key = get_vector_key(normalization, bin_size, unit, chr_index);
    auto it_vector = normalization_vectors.find(key);
    if (it_vector == normalization_vectors.end()) {
        throw std::runtime_error("normalization vector " + key + " not found");
    }
    const NormalizationVector& vector = it_vector->second;
    ByteArray buffer = file.read(vector.byte_count, vector.position);
    if (version > 8) {
        i64 value_count = buffer.read<i64>(0);
        return buffer.read_array<f32>(value_count, 8);
    } else {
        i32 value_count = buffer.read<i32>(0);
        std::vector<f64> values = buffer.read_array<f64>(value_count, 4);
        return std::vector<f32>(values.begin(), values.end());
    }
}
