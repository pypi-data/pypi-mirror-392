#include "util/main.cpp"

// Constants for BAM index
constexpr u32 BAM_MAGIC_BIN = 37450;  // Pseudo-bin for metadata

// Represents a chunk in a BAM index bin
struct BAMChunk {
    u64 chunk_beg;  // Virtual file offset of the start of the chunk
    u64 chunk_end;  // Virtual file offset of the end of the chunk
};

// Represents a bin in the BAM binning index
struct BAMBin {
    u32 bin;                        // Bin number
    std::vector<BAMChunk> chunks;   // List of chunks in this bin
};

// Represents the index for one reference sequence
struct BAMReferenceIndex {
    std::vector<BAMBin> bins;       // Binning index: list of distinct bins
    std::vector<u64> intervals;     // Linear index: 16kbp intervals
    
    // Optional metadata pseudo-bin (bin 37450)
    bool has_metadata = false;
    u64 ref_beg = 0;                // Start of reads placed on this reference
    u64 ref_end = 0;                // End of reads placed on this reference
    u64 n_mapped = 0;               // Number of mapped read-segments
    u64 n_unmapped = 0;             // Number of unmapped read-segments
};


class BAMIndex {
public:
    std::vector<BAMReferenceIndex> references;      // Index for each reference
    u64 n_no_coor = 0;                              // Optional: unplaced unmapped reads
    bool has_n_no_coor = false;                     // Whether n_no_coor is present

    BAMIndex(str path) {
        auto file = open_file(path);
        ByteStream stream = file->to_stream(0);
        
        // Read magic string (4 bytes: "BAI\1")
        ByteArray magic_bytes = stream.read(4);
        if (magic_bytes.to_string() != "BAI\1") {
            throw std::runtime_error("Invalid BAM index magic: expected BAI\\1");
        }
        
        // Read number of reference sequences
        u32 n_ref = stream.read<u32>();
        references.reserve(n_ref);
        
        // Read index for each reference sequence
        for (u32 ref_idx = 0; ref_idx < n_ref; ++ref_idx) {
            BAMReferenceIndex ref_index;
            
            // Read number of distinct bins
            u32 n_bin = stream.read<u32>();
            ref_index.bins.reserve(n_bin);
            
            // Read each bin
            for (u32 bin_idx = 0; bin_idx < n_bin; ++bin_idx) {
                BAMBin bin;
                bin.bin = stream.read<u32>();
                
                // Check if this is the metadata pseudo-bin
                if (bin.bin == BAM_MAGIC_BIN) {
                    // Read metadata pseudo-bin
                    u32 n_chunk = stream.read<u32>();
                    if (n_chunk != 2) {
                        throw std::runtime_error("Metadata pseudo-bin should have exactly 2 chunks");
                    }
                    
                    ref_index.has_metadata = true;
                    ref_index.ref_beg = stream.read<u64>();
                    ref_index.ref_end = stream.read<u64>();
                    ref_index.n_mapped = stream.read<u64>();
                    ref_index.n_unmapped = stream.read<u64>();
                } else {
                    // Read regular bin chunks
                    u32 n_chunk = stream.read<u32>();
                    bin.chunks.reserve(n_chunk);
                    
                    for (u32 chunk_idx = 0; chunk_idx < n_chunk; ++chunk_idx) {
                        BAMChunk chunk;
                        chunk.chunk_beg = stream.read<u64>();
                        chunk.chunk_end = stream.read<u64>();
                        bin.chunks.push_back(chunk);
                    }
                    
                    ref_index.bins.push_back(std::move(bin));
                }
            }
            
            // Read number of 16kbp intervals for linear index
            u32 n_intv = stream.read<u32>();
            ref_index.intervals.reserve(n_intv);
            
            // Read linear index intervals
            for (u32 intv_idx = 0; intv_idx < n_intv; ++intv_idx) {
                u64 ioffset = stream.read<u64>();
                ref_index.intervals.push_back(ioffset);
            }
            
            references.push_back(std::move(ref_index));
        }
        
        // Try to read optional n_no_coor (unplaced unmapped reads count)
        // This is at the end of the file and may not be present
        // Try to read another 8 bytes
        ByteArray no_coor_bytes = stream.read(8, true);
        if (no_coor_bytes.size() == 8) {
            n_no_coor = no_coor_bytes.read<u64>(0);
            has_n_no_coor = true;
        } else {
            // n_no_coor is optional, so it's okay if it's not present
            has_n_no_coor = false;
        }
        
    }

    // Helper function: calculate bin given an alignment covering [beg, end) (zero-based, half-closed-half-open)
    inline i32 reg2bin(i32 beg, i32 end) {
        --end;
        if (beg >> 14 == end >> 14) return ((1 << 15) - 1) / 7 + (beg >> 14);
        if (beg >> 17 == end >> 17) return ((1 << 12) - 1) / 7 + (beg >> 17);
        if (beg >> 20 == end >> 20) return ((1 << 9) - 1) / 7 + (beg >> 20);
        if (beg >> 23 == end >> 23) return ((1 << 6) - 1) / 7 + (beg >> 23);
        if (beg >> 26 == end >> 26) return ((1 << 3) - 1) / 7 + (beg >> 26);
        return 0;
    }


};




// Helper function: calculate the list of bins that may overlap with region [beg, end) (zero-based)
inline i32 reg2bins(i32 beg, i32 end, std::vector<u16>& list) {
    i32 i = 0;
    --end;
    
    list.push_back(0);
    ++i;
    
    for (i32 k = 1 + (beg >> 26); k <= 1 + (end >> 26); ++k) {
        list.push_back(static_cast<u16>(k));
        ++i;
    }
    for (i32 k = 9 + (beg >> 23); k <= 9 + (end >> 23); ++k) {
        list.push_back(static_cast<u16>(k));
        ++i;
    }
    for (i32 k = 73 + (beg >> 20); k <= 73 + (end >> 20); ++k) {
        list.push_back(static_cast<u16>(k));
        ++i;
    }
    for (i32 k = 585 + (beg >> 17); k <= 585 + (end >> 17); ++k) {
        list.push_back(static_cast<u16>(k));
        ++i;
    }
    for (i32 k = 4681 + (beg >> 14); k <= 4681 + (end >> 14); ++k) {
        list.push_back(static_cast<u16>(k));
        ++i;
    }
    
    return i;
}
