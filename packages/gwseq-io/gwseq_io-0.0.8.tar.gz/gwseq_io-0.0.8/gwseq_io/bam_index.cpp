#include "util/main.cpp"

constexpr u32 BAM_MAGIC_BIN = 37450;  // Pseudo-bin for metadata


// represents a chunk in a BAM index bin
struct BAMChunk {
    u64 start; // virtual file offset of the start of the chunk
    u64 end; // virtual file offset of the end of the chunk
};


// represents a bin in the BAM binning index
struct BAMIndexBin {
    u32 bin; // bin number
    std::vector<BAMChunk> chunks; // list of chunks in this bin
};


// represents the index for one reference sequence
struct BAMRefIndex {
    std::vector<BAMIndexBin> bins; // binning index: list of distinct bins
    std::vector<u64> intervals; // linear index: 16kbp intervals
    
    // optional metadata pseudo-bin (bin 37450)
    bool has_metadata = false;
    u64 ref_start = 0; // start of reads placed on this reference
    u64 ref_end = 0; // end of reads placed on this reference
    u64 n_mapped = 0; // number of mapped read-segments
    u64 n_unmapped = 0; // number of unmapped read-segments
};


class BAMIndex {
public:
    std::vector<BAMRefIndex> refs; // index for each reference
    u64 n_no_coor = 0; // unplaced unmapped reads (optional)
    bool has_n_no_coor = false; // whether n_no_coor is present

    BAMIndex(str path) {
        auto file = open_file(path);
        ByteStream stream = file->to_stream(0);
        
        // read magic string (4 bytes: "BAI\1")
        if (stream.read(4).to_string() != "BAI\1") {
            throw std::runtime_error("invalid bam index magic");
        }
        
        // read number of reference sequences
        u32 n_ref = stream.read<u32>();
        refs.reserve(n_ref);
        
        // read index for each reference sequence
        for (u32 ref_idx = 0; ref_idx < n_ref; ++ref_idx) {
            BAMRefIndex ref_index;
            
            // read number of distinct bins
            u32 n_bin = stream.read<u32>();
            ref_index.bins.reserve(n_bin);
            for (u32 bin_idx = 0; bin_idx < n_bin; ++bin_idx) {
                BAMIndexBin bin;
                bin.bin = stream.read<u32>();
                
                // check if this is the metadata pseudo-bin
                if (bin.bin == BAM_MAGIC_BIN) {
                    // read metadata pseudo-bin
                    u32 n_chunk = stream.read<u32>();
                    if (n_chunk != 2) throw std::runtime_error("invalid metadata pseudo-bin");
                    ref_index.has_metadata = true;
                    ref_index.ref_start = stream.read<u64>();
                    ref_index.ref_end = stream.read<u64>();
                    ref_index.n_mapped = stream.read<u64>();
                    ref_index.n_unmapped = stream.read<u64>();
                } else {
                    // read regular bin chunks
                    u32 n_chunk = stream.read<u32>();
                    bin.chunks.reserve(n_chunk);
                    for (u32 chunk_idx = 0; chunk_idx < n_chunk; ++chunk_idx) {
                        BAMChunk chunk;
                        chunk.start = stream.read<u64>();
                        chunk.end = stream.read<u64>();
                        bin.chunks.push_back(chunk);
                    }
                    ref_index.bins.push_back(std::move(bin));
                }
            }
            
            // read number of 16kb intervals for linear index
            u32 n_intv = stream.read<u32>();
            ref_index.intervals.reserve(n_intv);
            for (u32 intv_idx = 0; intv_idx < n_intv; ++intv_idx) {
                u64 ioffset = stream.read<u64>();
                ref_index.intervals.push_back(ioffset);
            }
            
            refs.push_back(std::move(ref_index));
        }
        
        // try to read optional n_no_coor (unplaced unmapped reads count)
        // this is at the end of the file and may not be present
        ByteArray no_coor_bytes = stream.read(8, true);
        if (no_coor_bytes.size() == 8) {
            n_no_coor = no_coor_bytes.read<u64>(0);
            has_n_no_coor = true;
        } else {
            has_n_no_coor = false;
        }
        
    }

    inline u64 get_overlapping_bin(u64 start, u64 end) {
        // compute bin given an alignment covering [beg, end)
        // zero-based, half-closed-half-open
        --end;
        if (start >> 14 == end >> 14) return ((1 << 15) - 1) / 7 + (start >> 14);
        if (start >> 17 == end >> 17) return ((1 << 12) - 1) / 7 + (start >> 17);
        if (start >> 20 == end >> 20) return ((1 << 9) - 1) / 7 + (start >> 20);
        if (start >> 23 == end >> 23) return ((1 << 6) - 1) / 7 + (start >> 23);
        if (start >> 26 == end >> 26) return ((1 << 3) - 1) / 7 + (start >> 26);
        return 0;
    }

    inline std::vector<u64> get_overlapping_bins(u64 start, u64 end) {
        // compute the list of bins that may overlap with region [beg, end)
        // zero-based, half-closed-half-open
        std::vector<u64> list;
        --end;
        list.push_back(0);
        for (u64 k = 1 + (start >> 26); k <= 1 + (end >> 26); ++k) {
            list.push_back(k);
        }
        for (u64 k = 9 + (start >> 23); k <= 9 + (end >> 23); ++k) {
            list.push_back(k);
        }
        for (u64 k = 73 + (start >> 20); k <= 73 + (end >> 20); ++k) {
            list.push_back(k);
        }
        for (u64 k = 585 + (start >> 17); k <= 585 + (end >> 17); ++k) {
            list.push_back(k);
        }
        for (u64 k = 4681 + (start >> 14); k <= 4681 + (end >> 14); ++k) {
            list.push_back(k);
        }
        return list;
    }

    // get chunks that overlap with a specified region
    std::vector<BAMChunk> get_overlapping_chunks(i64 ref_idx, i64 start, i64 end) {
        if (ref_idx < 0 || ref_idx >= static_cast<i64>(refs.size())) {
            throw std::runtime_error("ref index " + std::to_string(ref_idx) + " out of range");
        }
        const BAMRefIndex& ref_index = refs[ref_idx];
        std::vector<BAMChunk> result;
        
        // get bins that overlap the region
        u64 bounded_start = static_cast<u64>(std::max<i64>(0, start));
        u64 bounded_end = static_cast<u64>(std::max<i64>(0, end));
        auto bin_list = get_overlapping_bins(bounded_start, bounded_end);
        
        // find minimum offset from linear index (16kbp windows)
        u64 min_offset = 0;
        if (!ref_index.intervals.empty()) {
            u64 window = bounded_start >> 14; // 16kb = 2^14
            if (window < ref_index.intervals.size()) {
                min_offset = ref_index.intervals[window];
            }
        }
        
        // collect chunks from overlapping bins
        for (u64 bin_num : bin_list) {
            for (const BAMIndexBin& bin : ref_index.bins) {
                if (bin.bin == bin_num) {
                    for (const BAMChunk& chunk : bin.chunks) {
                        // only include chunks that end after min_offset
                        if (chunk.end >= min_offset) result.push_back(chunk);
                    }
                    break;
                }
            }
        }
        
        // sort chunks by start offset
        std::sort(result.begin(), result.end(), [](const BAMChunk& a, const BAMChunk& b) {
            return a.start < b.start;
        });
        
        // merge overlapping/adjacent chunks
        if (result.size() > 1) {
            std::vector<BAMChunk> merged;
            merged.push_back(result[0]);
            for (size_t i = 1; i < result.size(); ++i) {
                BAMChunk& last = merged.back();
                const BAMChunk& current = result[i];
                if (current.start <= last.end) {
                    // overlapping or adjacent - merge
                    last.end = std::max(last.end, current.end);
                } else {
                    merged.push_back(current);
                }
            }
            result = std::move(merged);
        }
        
        return result;
    }





};
