#include "util/main.cpp"


class BAMReader {
    str path;
    i64 parallel;
    str index_path;
    FilePool file_pool;

public:
    std::unique_ptr<BAMIndex> index;

    SAMHeader header;
    OrderedMap<str, ChrItem> chr_map;

    BAMReader(
        str path,
        i64 parallel = 1,
        i64 file_buffer_size = 32768,
        i64 max_file_buffer_count = 128,
        str index_path = ""
    ) : path(path),
        parallel(parallel),
        index_path(index_path),
        file_pool(path, "r", parallel, file_buffer_size, max_file_buffer_count)
    {   
        auto file = file_pool.get_pseudo_file();
        auto [h, c] = read_bam_header(file);
        header = std::move(h);
        chr_map = std::move(c);
        if (index_path == "") index_path = path + ".bai";
        try {
            index = std::make_unique<BAMIndex>(index_path);
        } catch (...) {
            index = nullptr;
        }
    }
    
    // get chunks that overlap with a specified region
    std::vector<BAMChunk> get_overlapping_chunks(str chr_id, i64 start, i64 end) {
        if (!index) throw std::runtime_error("bam file is not indexed");
        i64 chr_idx = chr_map.at(chr_id).index;
        return index->get_overlapping_chunks(chr_idx, start, end);
    }

    ByteArray decompress_chunks(const std::vector<BAMChunk>& chunks) {
        ByteArray data;
        auto file = file_pool.get_pseudo_file();
        for (const auto& chunk : chunks) {
            i64 file_offset = static_cast<i64>(chunk.start >> 16);
            i64 block_offset = static_cast<i64>(chunk.start & 0xFFFF);
            i64 end_file_offset = static_cast<i64>(chunk.end >> 16);
            i64 end_block_offset = static_cast<i64>(chunk.end & 0xFFFF);
            i64 size = (end_file_offset - file_offset) + 65536;
            ByteArray chunk_raw_data = file.read(size, file_offset);
            std::vector<ByteArray> blocks;
            i64 index = 0;
            while (true) {
                u16 block_size = chunk_raw_data.read<u16>(index + 16) + 1;
                if (index + block_size >= chunk_raw_data.size()) break;
                ByteArray raw_block = chunk_raw_data.sliced(index, block_size);
                ByteArray block = raw_block.decompressed();
                blocks.push_back(std::move(block));
                index += block_size;
            }
            if (blocks.size() == 1) {
                blocks[0] = blocks[0].sliced(block_offset, end_block_offset - block_offset);
            } else {
                blocks[0] = blocks[0].sliced(block_offset, blocks[0].size() - block_offset);
                blocks[blocks.size() - 1] = blocks[blocks.size() - 1].sliced(0, end_block_offset);
            }
            for (const auto& block : blocks) {
                data.append(block);
            }
        }
        return data;
    }





};

