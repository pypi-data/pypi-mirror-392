struct MatrixMetadata {
    i64 chr1_index;
    i64 chr2_index;
    str unit;
    i64 bin_size;
    f32 sum_counts;
    i64 block_bin_count;
    i64 block_column_count;
    OrderedMap<i64, HiCIndexItem> blocks;
};


str get_matrix_key(
    i64 chr1_index,
    i64 chr2_index,
    i64 bin_size,
    const str& unit
) {
    str key = 
        "chr_index=" + std::to_string(chr1_index) + "_" + std::to_string(chr2_index) + "|" +
        "bin_size=" + std::to_string(bin_size) + "|" +
        "unit=" + unit;
    return key;
}


std::list<MatrixMetadata> get_matrix_metadata_from_file(
    File& file,
    i64 position,
    i64 chr1_index,
    i64 chr2_index
) {
    ByteStream stream = file.to_stream(position);
    auto buffer_chr1_index = static_cast<i64>(stream.read<i32>());
    auto buffer_chr2_index = static_cast<i64>(stream.read<i32>());
    auto bin_size_count = static_cast<i64>(stream.read<i32>());
    if (buffer_chr1_index != chr1_index || buffer_chr2_index != chr2_index) {
        throw std::runtime_error("matrix metadata chr indices mismatch");
    }
    std::list<MatrixMetadata> matrices;
    for (i64 i = 0; i < bin_size_count; ++i) {
        MatrixMetadata matrix;
        matrix.chr1_index = buffer_chr1_index;
        matrix.chr2_index = buffer_chr2_index;
        matrix.unit = to_lowercase(stream.read_until('\0').to_string());
        (void)stream.read<i32>(); // bin size index in header
        matrix.sum_counts = stream.read<f32>();
        (void)stream.read<i32>(); // occupied cell count
        (void)stream.read<f32>(); // 5th percentile estimate of counts
        (void)stream.read<f32>(); // 95th percentile estimate of counts
        matrix.bin_size = static_cast<i64>(stream.read<i32>());
        matrix.block_bin_count = static_cast<i64>(stream.read<i32>());
        matrix.block_column_count = static_cast<i64>(stream.read<i32>());
        i64 block_count = static_cast<i64>(stream.read<i32>());
        for (i64 j = 0; j < block_count; ++j) {
            HiCIndexItem block;
            i64 block_number = static_cast<i64>(stream.read<i32>());
            block.position = stream.read<i64>();
            block.size = static_cast<i64>(stream.read<i32>());
            matrix.blocks.insert(block_number, block);
        }
        matrices.push_back(std::move(matrix));
    }
    return matrices;
}
