#include "util/main.cpp"


class BAMReader {
    str path;
    i64 parallel;
    FilePool file_pool;
    BAMIndex index;

public:
    BAMReader(
        str path,
        i64 parallel = 1,
        i64 file_buffer_size = 32768,
        i64 max_file_buffer_count = 128
    ) : path(path), parallel(parallel),
        file_pool(path, "r", parallel, file_buffer_size, max_file_buffer_count) {
        // Load the BAM index (.bai file)
        str index_path = path + ".bai";
        index = read_bam_index(index_path);
    }
    
    // Get chunks that overlap with a specified region
    std::vector<BAMChunk> get_overlapping_chunks(i32 ref_id, i32 beg, i32 end) {
        if (ref_id < 0 || ref_id >= static_cast<i32>(index.references.size())) {
            throw std::runtime_error("Invalid reference ID: " + std::to_string(ref_id));
        }
        
        const BAMReferenceIndex& ref_index = index.references[ref_id];
        std::vector<BAMChunk> result;
        
        // Get bins that overlap the region
        std::vector<u16> bin_list;
        reg2bins(beg, end, bin_list);
        
        // Find minimum offset from linear index (16kbp windows)
        u64 min_offset = 0;
        if (!ref_index.intervals.empty()) {
            i32 window = beg >> 14;  // 16kbp = 2^14
            if (window < static_cast<i32>(ref_index.intervals.size())) {
                min_offset = ref_index.intervals[window];
            }
        }
        
        // Collect chunks from overlapping bins
        for (u16 bin_num : bin_list) {
            for (const BAMBin& bin : ref_index.bins) {
                if (bin.bin == bin_num) {
                    for (const BAMChunk& chunk : bin.chunks) {
                        // Only include chunks that end after min_offset
                        if (chunk.chunk_end >= min_offset) {
                            result.push_back(chunk);
                        }
                    }
                    break;
                }
            }
        }
        
        // Sort chunks by start offset
        std::sort(result.begin(), result.end(), [](const BAMChunk& a, const BAMChunk& b) {
            return a.chunk_beg < b.chunk_beg;
        });
        
        // Merge overlapping/adjacent chunks
        if (result.size() > 1) {
            std::vector<BAMChunk> merged;
            merged.push_back(result[0]);
            
            for (size_t i = 1; i < result.size(); ++i) {
                BAMChunk& last = merged.back();
                const BAMChunk& current = result[i];
                
                if (current.chunk_beg <= last.chunk_end) {
                    // Overlapping or adjacent - merge
                    last.chunk_end = std::max(last.chunk_end, current.chunk_end);
                } else {
                    merged.push_back(current);
                }
            }
            
            result = std::move(merged);
        }
        
        return result;
    }
};

