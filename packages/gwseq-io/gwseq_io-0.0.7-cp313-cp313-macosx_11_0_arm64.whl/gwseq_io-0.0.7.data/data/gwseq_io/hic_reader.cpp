class HiCReader {
    str path;
    i64 parallel;
    FilePool file_pool;
    OrderedMap<str, std::shared_ptr<std::vector<f32>>> cached_expected_values;
    OrderedMap<str, std::shared_ptr<std::vector<f32>>> cached_normalization_vectors;
    OrderedMap<str, std::shared_ptr<MatrixMetadata>> cached_matrices_metadata;
    i64 max_cached_expected_values_size = 32;
    i64 max_cached_normalization_vectors_size = 32;
    i64 max_cached_matrices_metadata_size = 64;

public:
    HiCHeader header;
    HiCFooter footer;
    
    HiCReader(
        const str& path,
        i64 parallel = 24,
        i64 file_buffer_size = 32768,
        i64 max_file_buffer_count = 128
    ) : path(path), parallel(parallel),
        file_pool(path, "r", parallel, file_buffer_size, max_file_buffer_count)
    {
        auto file = file_pool.get_pseudo_file();
        header = read_hic_header(file);
        footer = read_hic_footer(file, header.version, header.footer_position);
    }

    std::shared_ptr<std::vector<f32>> get_expected_values(
        i64 chr_index,
        const str& normalization,
        i64 bin_size,
        const str& unit
    ) {
        str key = get_vector_key(normalization, bin_size, unit, chr_index);
        auto it_vector = cached_expected_values.find(key);
        if (it_vector != cached_expected_values.end()) {
            return it_vector->second;
        }
        while (cached_expected_values.size() >= max_cached_expected_values_size) {
            cached_expected_values.pop_front();
        }
        auto vector = compute_expected_values(
            footer.expected_value_vectors,
            normalization, bin_size, unit, chr_index
        );
        auto vector_ptr = std::make_shared<std::vector<f32>>(std::move(vector));
        cached_expected_values.insert(key, vector_ptr);
        return vector_ptr;
    }

    std::shared_ptr<std::vector<f32>> get_normalization_vector(
        i64 chr_index,
        const str& normalization,
        i64 bin_size,
        const str& unit
    ) {
        str key = get_vector_key(normalization, bin_size, unit, chr_index);
        auto it_vector = cached_normalization_vectors.find(key);
        if (it_vector != cached_normalization_vectors.end()) {
            return it_vector->second;
        }
        while (cached_normalization_vectors.size() >= max_cached_normalization_vectors_size) {
            cached_normalization_vectors.pop_front();
        }
        auto file = file_pool.get_pseudo_file();
        auto vector = get_normalization_vector_from_file(
            file, header.version, footer.normalization_vectors,
            chr_index, normalization, bin_size, unit
        );
        auto vector_ptr = std::make_shared<std::vector<f32>>(std::move(vector));
        cached_normalization_vectors.insert(key, vector_ptr);
        return vector_ptr;
    }

    std::shared_ptr<MatrixMetadata> get_matrix_metadata(
        i64 chr1_index,
        i64 chr2_index,
        i64 bin_size,
        const str& unit
    ) {
        str key = get_matrix_key(chr1_index, chr2_index, bin_size, unit);
        auto it_matrix = cached_matrices_metadata.find(key);
        if (it_matrix != cached_matrices_metadata.end()) {
            return it_matrix->second;
        }
        while (cached_matrices_metadata.size() >= max_cached_matrices_metadata_size) {
            cached_matrices_metadata.pop_front();
        }
        str chr_key = std::to_string(chr1_index) + "_" + std::to_string(chr2_index);
        auto it_master_index = footer.master_index.find(chr_key);
        if (it_master_index == footer.master_index.end()) {
            throw std::runtime_error("no matrix metadata for " + chr_key);
        }
        auto file = file_pool.get_pseudo_file();
        auto position = it_master_index->second.position;
        for (auto matrix : get_matrix_metadata_from_file(file, position, chr1_index, chr2_index)) {
            auto matrix_key = get_matrix_key(matrix.chr1_index, matrix.chr2_index, matrix.bin_size, matrix.unit);
            auto matrix_ptr = std::make_shared<MatrixMetadata>(std::move(matrix));
            cached_matrices_metadata.insert(matrix_key, matrix_ptr);
        }
        it_matrix = cached_matrices_metadata.find(key);
        if (it_matrix == cached_matrices_metadata.end()) {
            throw std::runtime_error("no matrix metadata for " + key);
        }
        return it_matrix->second;
    }

    std::vector<i64> get_available_bin_sizes(const str& unit) {
        if (to_lowercase(unit) == "bp") {
            return header.bp_resolutions;
        } else if (to_lowercase(unit) == "frag") {
            return header.frag_resolutions;
        } else {
            throw std::runtime_error("unit " + unit + " invalid (bp or frag)");
        }
    }

    Loc2D parse_loc(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        i64 bin_size = -1,
        i64 bin_count = -1,
        bool full_bin = false,
        const str& unit = "bp"
    ) {
        auto [preparsed_starts, preparsed_ends] = preparse_locs(chr_ids, starts, ends, centers, span);
        return parse_loc2d(
            header.chr_map, get_available_bin_sizes(unit),
            chr_ids, preparsed_starts, preparsed_ends,
            bin_size, bin_count, full_bin
        );
    }

    ContactRecordGenerator iter_records(
        const Loc2D& loc,
        i64 min_distance_from_diagonal = -1,
        i64 max_distance_from_diagonal = -1,
        str normalization = "none",
        str mode = "observed",
        str unit = "bp"

    ) {
        normalization = to_lowercase(normalization);
        mode = to_lowercase(mode);
        unit = to_lowercase(unit);
        std::shared_ptr<std::vector<f32>> x_normalization_vector = nullptr;
        std::shared_ptr<std::vector<f32>> y_normalization_vector = nullptr;
        std::shared_ptr<std::vector<f32>> expected_values = nullptr;
        if (normalization != "none") {
            x_normalization_vector = get_normalization_vector(
                loc.x.chr.index, normalization, loc.bin_size, unit
            );
            y_normalization_vector = get_normalization_vector(
                loc.y.chr.index, normalization, loc.bin_size, unit
            );
        }
        if ((mode == "oe" || mode == "expected") && loc.x.chr.index == loc.y.chr.index) {
            expected_values = get_expected_values(
                loc.x.chr.index, normalization, loc.bin_size, unit
            );
        }
        auto matrix_metadata = get_matrix_metadata(
            loc.x.chr.index, loc.y.chr.index, loc.bin_size, unit
        );
        f32 average_value = loc.x.chr.index == loc.y.chr.index
            ? std::numeric_limits<f32>::quiet_NaN()
            : matrix_metadata->sum_counts / (loc.x.chr.size / loc.bin_size) / (loc.y.chr.size / loc.bin_size);
        auto block_numbers = get_blocks_numbers(
            loc,
            matrix_metadata->block_bin_count,
            matrix_metadata->block_column_count,
            max_distance_from_diagonal,
            header.version
        );
        std::vector<HiCIndexItem> blocks;
        blocks.reserve(block_numbers.size());
        for (const auto& block_number : block_numbers) {
            auto block_it = matrix_metadata->blocks.find(block_number);
            if (block_it == matrix_metadata->blocks.end()) continue;
            blocks.push_back(block_it->second);
        }
        blocks.shrink_to_fit();
        return ContactRecordGenerator(
            file_pool, header.version, parallel,
            blocks, loc,
            normalization, mode, unit,
            x_normalization_vector, y_normalization_vector,
            expected_values, average_value,
            min_distance_from_diagonal, max_distance_from_diagonal
        );
    }

    std::vector<f32> read_signal(
        const Loc2D& loc,
        f32 def_value = 0.0f,
        bool triangle = false,
        i64 min_distance_from_diagonal = -1,
        i64 max_distance_from_diagonal = -1,
        const str& normalization = "none",
        const str& mode = "observed",
        const str& unit = "bp"
    ) {
        auto generator = iter_records(
            loc,
            min_distance_from_diagonal, max_distance_from_diagonal,
            normalization, mode, unit
        );
        i64 row_count = loc.x.bin_end - loc.x.bin_start;
        i64 col_count = loc.y.bin_end - loc.y.bin_start;
        std::vector<f32> signal(row_count * col_count, def_value);
        for (const auto& records : generator) {
            for (const auto& record : records) {
                i64 r = record.x_bin - loc.x.bin_start;
                i64 c = record.y_bin - loc.y.bin_start;
                if (r >= 0 && r < row_count && c >= 0 && c < col_count) {
                    signal[r * col_count + c] = record.value;
                }
                if (loc.x.chr.index == loc.y.chr.index && !triangle) {
                    i64 r_sym = record.y_bin - loc.x.bin_start;
                    i64 c_sym = record.x_bin - loc.y.bin_start;
                    if (r_sym >= 0 && r_sym < row_count && c_sym >= 0 && c_sym < col_count) {
                        signal[r_sym * col_count + c_sym] = record.value;
                    }
                }
            }
        }
        if (loc.reversed) {
            std::vector<f32> transposed_signal(signal.size());
            for (i64 r = 0; r < row_count; ++r) {
                for (i64 c = 0; c < col_count; ++c) {
                    transposed_signal[c * row_count + r] = signal[r * col_count + c];
                }
            }
            signal = std::move(transposed_signal);
        }
        return signal;
    }

    Sparse2DArray<f32> read_sparse_signal(
        const Loc2D& loc,
        bool triangle = false,
        i64 min_distance_from_diagonal = -1,
        i64 max_distance_from_diagonal = -1,
        const str& normalization = "none",
        const str& mode = "observed",
        const str& unit = "bp"
    ) {
        auto generator = iter_records(
            loc,
            min_distance_from_diagonal, max_distance_from_diagonal,
            normalization, mode, unit
        );
        i64 row_count = loc.x.bin_end - loc.x.bin_start;
        i64 col_count = loc.y.bin_end - loc.y.bin_start;
        Sparse2DArray<f32> signal;
        signal.shape = {static_cast<u32>(row_count), static_cast<u32>(col_count)};
        for (const auto& records : generator) {
            std::vector<f32> batch_signal;
            std::vector<u32> batch_row;
            std::vector<u32> batch_col;
            batch_signal.reserve(records.size());
            batch_row.reserve(records.size());
            batch_col.reserve(records.size());
            for (const auto& record : records) {
                i64 r = record.x_bin - loc.x.bin_start;
                i64 c = record.y_bin - loc.y.bin_start;
                if (r >= 0 && r < row_count && c >= 0 && c < col_count) {
                    batch_signal.push_back(record.value);
                    batch_row.push_back(static_cast<u32>(r));
                    batch_col.push_back(static_cast<u32>(c));
                }
                if (loc.x.chr.index == loc.y.chr.index && !triangle) {
                    i64 r_sym = record.y_bin - loc.x.bin_start;
                    i64 c_sym = record.x_bin - loc.y.bin_start;
                    if (r_sym >= 0 && r_sym < row_count && c_sym >= 0 && c_sym < col_count) {
                        batch_signal.push_back(record.value);
                        batch_row.push_back(static_cast<u32>(r_sym));
                        batch_col.push_back(static_cast<u32>(c_sym));
                    }
                }
            }
            signal.values.insert(signal.values.end(), batch_signal.begin(), batch_signal.end());
            signal.row.insert(signal.row.end(), batch_row.begin(), batch_row.end());
            signal.col.insert(signal.col.end(), batch_col.begin(), batch_col.end());
        }
        // Sort sparse matrix entries by row index first, then by column index
        if (!signal.values.empty()) {
            std::vector<size_t> indices(signal.values.size());
            std::iota(indices.begin(), indices.end(), 0);
            std::sort(indices.begin(), indices.end(),
                [&signal](size_t i1, size_t i2) {
                    if (signal.row[i1] != signal.row[i2]) {
                        return signal.row[i1] < signal.row[i2];
                    } else {
                        return signal.col[i1] < signal.col[i2];
                    }
                }
            );
            std::vector<f32> sorted_values(signal.values.size());
            std::vector<u32> sorted_row(signal.row.size());
            std::vector<u32> sorted_col(signal.col.size());
            for (size_t i = 0; i < indices.size(); ++i) {
                sorted_values[i] = signal.values[indices[i]];
                sorted_row[i] = signal.row[indices[i]];
                sorted_col[i] = signal.col[indices[i]];
            }
            signal.values = std::move(sorted_values);
            signal.row = std::move(sorted_row);
            signal.col = std::move(sorted_col);
        }
        if (loc.reversed) {
            std::vector<u32> transposed_row = signal.col;
            std::vector<u32> transposed_col = signal.row;
            signal.row = std::move(transposed_row);
            signal.col = std::move(transposed_col);
            signal.shape = {signal.shape[1], signal.shape[0]};
        }
        return signal;
    }

};
