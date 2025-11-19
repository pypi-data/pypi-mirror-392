i64 get_distance_from_diagonal(i64 x, i64 y, const Loc2D& loc) {
    if (loc.x.chr.index == loc.y.chr.index) {
        return std::abs(y - x);
    } else {
        f64 a = static_cast<f64>(loc.y.binned_end - loc.y.binned_start) /
            (loc.x.binned_end - loc.x.binned_start);
        f64 b = loc.y.binned_start - a * loc.x.binned_start;
        f64 vertical = std::abs(y - (a * x + b));
        f64 horizontal = std::abs(x - (y - b) / a);
        return static_cast<i64>(std::round(std::min(vertical, horizontal)));
    }
}


std::set<i64> get_blocks_numbers(
    const Loc2D& loc,
    i64 block_bin_count,
    i64 block_column_count,
    i64 max_distance_from_diagonal,
    i64 version
) {
    std::set<i64> blocks_set;
    if (version > 8 && loc.x.chr.index == loc.y.chr.index) {
        i64 translated_lower_pad = (loc.x.bin_start + loc.y.bin_start) / 2 / block_bin_count;
        i64 translated_higher_pad = (loc.x.bin_end + loc.y.bin_end) / 2 / block_bin_count + 1;
        i64 translated_nearer_depth = static_cast<i64>(std::log2(
            1 + abs(loc.x.bin_start - loc.y.bin_end) / std::sqrt(2) / block_bin_count));
        i64 translated_further_depth = static_cast<i64>(std::log2(
            1 + abs(loc.x.bin_end - loc.y.bin_start) / std::sqrt(2) / block_bin_count));
        i64 nearer_depth = std::min(translated_nearer_depth, translated_further_depth);
        if ((loc.x.bin_start > loc.y.bin_end && loc.x.bin_end < loc.y.bin_start) ||
            (loc.x.bin_end > loc.y.bin_start && loc.x.bin_start < loc.y.bin_end)) {
            nearer_depth = 0;
        }
        i64 further_depth = std::max(translated_nearer_depth, translated_further_depth) + 1;
        for (i64 depth = nearer_depth; depth <= further_depth; depth++) {
            for (i64 pad = translated_lower_pad; pad <= translated_higher_pad; pad++) {
                i64 block_number = depth * block_column_count + pad;
                blocks_set.insert(block_number);
            }
        }
    } else {
        i64 col1 = loc.x.bin_start / block_bin_count;
        i64 col2 = loc.x.bin_end / block_bin_count;
        i64 row1 = loc.y.bin_start / block_bin_count;
        i64 row2 = loc.y.bin_end / block_bin_count;
        for (i64 r = row1; r <= row2; r++) {
            for (i64 c = col1; c <= col2; c++) {
                if (max_distance_from_diagonal >= 0) {
                    i64 r_start = r * block_bin_count * loc.bin_size;
                    i64 c_start = c * block_bin_count * loc.bin_size;
                    i64 r_end = r_start + block_bin_count * loc.bin_size;
                    i64 c_end = c_start + block_bin_count * loc.bin_size;
                    i64 min_dist = std::min({ 
                        get_distance_from_diagonal(r_start, c_start, loc),
                        get_distance_from_diagonal(r_end, c_start, loc),
                        get_distance_from_diagonal(r_start, c_end, loc),
                        get_distance_from_diagonal(r_end, c_end, loc)
                    });
                    if (min_dist > max_distance_from_diagonal) continue;
                }
                i64 block_number = r * block_column_count + c;
                blocks_set.insert(block_number);
            }
        }
        if (loc.x.chr.index == loc.y.chr.index) {
            for (i64 r = col1; r <= col2; r++) {
                for (i64 c = row1; c <= row2; c++) {
                    if (max_distance_from_diagonal >= 0) {
                        i64 r_start = r * block_bin_count * loc.bin_size;
                        i64 c_start = c * block_bin_count * loc.bin_size;
                        i64 r_end = r_start + block_bin_count * loc.bin_size;
                        i64 c_end = c_start + block_bin_count * loc.bin_size;
                        i64 min_dist = std::min({ 
                            get_distance_from_diagonal(r_start, c_start, loc),
                            get_distance_from_diagonal(r_end, c_start, loc),
                            get_distance_from_diagonal(r_start, c_end, loc),
                            get_distance_from_diagonal(r_end, c_end, loc)
                        });
                        if (min_dist > max_distance_from_diagonal) continue;
                    }
                    i32 block_number = r * block_column_count + c;
                    blocks_set.insert(block_number);
                }
            }
        }
    }
    return blocks_set;
}


struct ContactRecord {
    i64 x_bin;
    i64 y_bin;
    f32 value;
};


bool process_record(
    ContactRecord& record,
    const Loc2D& loc,
    const str& normalization,
    const str& mode,
    const str& unit,
    const std::shared_ptr<std::vector<f32>>& x_normalization_vector,
    const std::shared_ptr<std::vector<f32>>& y_normalization_vector,
    const std::shared_ptr<std::vector<f32>>& expected_values,
    f32 average_value,
    i64 min_distance_from_diagonal,
    i64 max_distance_from_diagonal
) {
    i64 x = record.x_bin * loc.bin_size;
    i64 y = record.y_bin * loc.bin_size;
    if (min_distance_from_diagonal >= 0 || max_distance_from_diagonal >= 0) {
        i64 distance = get_distance_from_diagonal(x, y, loc);
        if (min_distance_from_diagonal >= 0 && distance < min_distance_from_diagonal) return false;
        if (max_distance_from_diagonal >= 0 && distance > max_distance_from_diagonal) return false;
    }
    if (!(((x >= loc.x.binned_start && x <= loc.x.binned_end &&
        y >= loc.y.binned_start && y <= loc.y.binned_end)) ||
        (loc.x.chr.index == loc.y.chr.index &&
        y >= loc.x.binned_start && y <= loc.x.binned_end && 
        x >= loc.y.binned_start && x <= loc.y.binned_end))) {
        return false;
    }
    if (normalization != "none") {
        f32 x_norm = (*x_normalization_vector)[record.x_bin];
        f32 y_norm = (*y_normalization_vector)[record.y_bin];
        record.value /= (x_norm * y_norm);
    }
    if (mode == "oe") {
        if (loc.x.chr.index == loc.y.chr.index) {
            size_t i = std::min(
                expected_values->size() - 1,
                static_cast<size_t>(std::abs(y - x) / loc.bin_size)
            );
            record.value /= (*expected_values)[i];
        } else {
            record.value /= average_value;
        }
    } else if (mode == "expected") {
        if (loc.x.chr.index == loc.y.chr.index) {
            size_t i = std::min(
                expected_values->size() - 1,
                static_cast<size_t>(std::abs(y - x) / loc.bin_size)
            );
            record.value = (*expected_values)[i];
        } else {
            record.value = average_value;
        }
    }
    return !(std::isnan(record.value) || std::isinf(record.value));
}


std::vector<ContactRecord> read_block(
    File& file,
    i64 version,
    HiCIndexItem block,
    const Loc2D& loc,
    const str& normalization,
    const str& mode,
    const str& unit,
    const std::shared_ptr<std::vector<f32>>& x_normalization_vector,
    const std::shared_ptr<std::vector<f32>>& y_normalization_vector,
    const std::shared_ptr<std::vector<f32>>& expected_values,
    f32 average_value,
    i64 min_distance_from_diagonal,
    i64 max_distance_from_diagonal
) {
    ByteArray buffer = file.read(block.size, block.position).decompressed();
    std::vector<ContactRecord> records;
    i64 record_count = static_cast<i64>(buffer.read<i32>(0));
    records.reserve(record_count);
    i64 offset = 4;
    if (version < 7) {
        for (i64 i = 0; i < record_count; ++i) {
            ContactRecord record;
            record.x_bin = static_cast<i64>(buffer.read<i32>(offset));
            record.y_bin = static_cast<i64>(buffer.read<i32>(offset + 4));
            record.value = buffer.read<f32>(offset + 8);
            bool include = process_record(
                record, loc, normalization, mode, unit,
                x_normalization_vector, y_normalization_vector,
                expected_values, average_value,
                min_distance_from_diagonal, max_distance_from_diagonal
            );
            if (include) records.push_back(record);
            offset += 12;
        }
        records.shrink_to_fit();
        return records;
    }
    i64 bin_column_offset = static_cast<i64>(buffer.read<i32>(offset));
    i64 bin_row_offset = static_cast<i64>(buffer.read<i32>(offset + 4));
    bool use_float = (buffer.read<u8>(offset + 8) == 1);
    bool use_int_x_pos = false;
    bool use_int_y_pos = false;
    if (version > 8) {
        use_int_x_pos = (buffer.read<u8>(offset + 9) == 1);
        use_int_y_pos = (buffer.read<u8>(offset + 10) == 1);
        offset += 11;
    } else {
        offset += 9;
    }
    u8 matrix_type = buffer.read<u8>(offset);
    offset += 1;
    if (matrix_type == 1) {
        i64 x_advance = use_int_x_pos ? 4 : 2;
        i64 y_advance = use_int_y_pos ? 4 : 2;
        i64 value_advance = use_float ? 4 : 2;
        i64 row_count = use_int_y_pos
            ? static_cast<i64>(buffer.read<i32>(offset))
            : static_cast<i64>(buffer.read<i16>(offset));
        offset += y_advance;
        for (i64 i = 0; i < row_count; ++i) {
            i64 row_number = use_int_y_pos
                ? static_cast<i64>(buffer.read<i32>(offset))
                : static_cast<i64>(buffer.read<i16>(offset));
            offset += y_advance;
            i64 col_count = use_int_x_pos
                ? static_cast<i64>(buffer.read<i32>(offset))
                : static_cast<i64>(buffer.read<i16>(offset));
            offset += x_advance;
            i64 y_bin = bin_row_offset + row_number;
            for (i64 j = 0; j < col_count; ++j) {
                i64 col_number = use_int_x_pos
                    ? static_cast<i64>(buffer.read<i32>(offset))
                    : static_cast<i64>(buffer.read<i16>(offset));
                offset += x_advance;
                i64 x_bin = bin_column_offset + col_number;
                f32 value = use_float
                    ? buffer.read<f32>(offset)
                    : static_cast<f32>(buffer.read<i16>(offset));
                offset += value_advance;
                ContactRecord record;
                record.x_bin = x_bin;
                record.y_bin = y_bin;
                record.value = value;
                bool include = process_record(
                    record, loc, normalization, mode, unit,
                    x_normalization_vector, y_normalization_vector,
                    expected_values, average_value,
                    min_distance_from_diagonal, max_distance_from_diagonal
                );
                if (include) records.push_back(record);
            }
        }
    } else if (matrix_type == 2) {
        i64 count = static_cast<i64>(buffer.read<i32>(offset));
        i64 width = static_cast<i64>(buffer.read<i16>(offset + 4));
        offset += 6;
        for (i64 i = 0; i < count; ++i) {
            i64 row = i / width;
            i64 col = i - row * width;
            i64 x_bin = bin_column_offset + col;
            i64 y_bin = bin_row_offset + row;
            f32 value;
            if (use_float) {
                value = buffer.read<f32>(offset);
                offset += 4;
                if (std::isnan(value)) continue;
            } else {
                i16 short_value = buffer.read<i16>(offset);
                offset += 2;
                if (short_value == -32768) continue;
                value = static_cast<f32>(short_value);
            }
            ContactRecord record;
            record.x_bin = x_bin;
            record.y_bin = y_bin;
            record.value = value;
            bool include = process_record(
                record, loc, normalization, mode, unit,
                x_normalization_vector, y_normalization_vector,
                expected_values, average_value,
                min_distance_from_diagonal, max_distance_from_diagonal
            );
            if (include) records.push_back(record);
        }
    } else {
        throw std::runtime_error("matrix type " + std::to_string(matrix_type) + " invalid");
    }
    records.shrink_to_fit();
    return records;
}


class ContactRecordGenerator : public GeneratorBase<ContactRecordGenerator, std::vector<ContactRecord>> {
    std::shared_ptr<ThreadPoolManager<std::vector<ContactRecord>, true>> thread_pool_manager;

public:
    ContactRecordGenerator(const ContactRecordGenerator&) = delete;
    ContactRecordGenerator& operator=(const ContactRecordGenerator&) = delete;
    ContactRecordGenerator(ContactRecordGenerator&&) = default;
    ContactRecordGenerator& operator=(ContactRecordGenerator&&) = default;

    ContactRecordGenerator(
        FilePool& file_pool,
        i64 version,
        i64 parallel,
        const std::vector<HiCIndexItem>& blocks,
        const Loc2D& loc,
        const str& normalization,
        const str& mode,
        const str& unit,
        const std::shared_ptr<std::vector<f32>>& x_normalization_vector,
        const std::shared_ptr<std::vector<f32>>& y_normalization_vector,
        const std::shared_ptr<std::vector<f32>>& expected_values,
        f32 average_value,
        i64 min_distance_from_diagonal,
        i64 max_distance_from_diagonal
    ) : thread_pool_manager(std::make_shared<ThreadPoolManager<std::vector<ContactRecord>, true>>(parallel)) {
        for (const auto& block : blocks) {
            thread_pool_manager->enqueue(
                [&file_pool, version, block, loc, normalization, mode, unit,
                 x_normalization_vector, y_normalization_vector, expected_values,
                 average_value, min_distance_from_diagonal, max_distance_from_diagonal]() {
                    auto file = file_pool.get_pseudo_file();
                    return read_block(
                        file, version, block, loc,
                        normalization, mode, unit,
                        x_normalization_vector, y_normalization_vector,
                        expected_values, average_value,
                        min_distance_from_diagonal, max_distance_from_diagonal
                    );
                }
            );
        }
    }

    NextResult next() {
        auto [value, done] = thread_pool_manager->next();
        return {std::move(value), done};
    }

};
