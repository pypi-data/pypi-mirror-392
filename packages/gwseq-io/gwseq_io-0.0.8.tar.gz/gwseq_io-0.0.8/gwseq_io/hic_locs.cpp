#pragma once


struct Loc2DLoc {
    ChrItem chr;
    i64 start;
    i64 end;
    i64 binned_start;
    i64 binned_end;
    i64 bin_start;
    i64 bin_end;
};


struct Loc2D {
    Loc2DLoc x;
    Loc2DLoc y;
    i64 bin_size;
    bool reversed = false;
};


Loc2D parse_loc2d(
    const OrderedMap<str, ChrItem>& chr_map,
    const std::vector<i64>& available_bin_sizes,
    std::vector<str> chr_ids,
    std::vector<i64> starts,
    std::vector<i64> ends,
    i64 bin_size = -1,
    i64 bin_count = -1,
    bool full_bin = false
) {
    if (chr_ids.size() == 1) {
        chr_ids.push_back(chr_ids[0]);
    } else if (chr_ids.size() != 2) {
        throw std::runtime_error("1 or 2 chromosomes must be specified");
    }
    if (starts.size() == 1) {
        starts.push_back(starts[0]);
    } else if (starts.size() != 2) {
        throw std::runtime_error("1 or 2 start positions must be specified");
    }
    if (ends.size() == 1) {
        ends.push_back(ends[0]);
    } else if (ends.size() != 2) {
        throw std::runtime_error("1 or 2 end positions must be specified");
    }
    Loc2D loc;
    loc.x.chr = parse_chr(chr_ids[0], chr_map);
    loc.x.start = starts[0];
    loc.x.end = ends[0];
    loc.y.chr = parse_chr(chr_ids[1], chr_map);
    loc.y.start = starts[1];
    loc.y.end = ends[1];
    if (loc.x.chr.index > loc.y.chr.index) {
        std::swap(loc.x, loc.y);
        loc.reversed = true;
    }
    if (bin_count >= 0) {
        i64 span = (loc.x.end - loc.x.start + loc.y.end - loc.y.start) / 2;
        i64 requested_bin_size = (span + bin_count - 1) / bin_count;
        bin_size = available_bin_sizes[0];
        i64 min_delta = std::abs(available_bin_sizes[0] - requested_bin_size);
        for (i64 available : available_bin_sizes) {
            i64 delta = std::abs(available - requested_bin_size);
            if (delta < min_delta) {
                min_delta = delta;
                bin_size = available;
            }
        }
    } else if (bin_size < 0) {
        bin_size = *std::min_element(available_bin_sizes.begin(), available_bin_sizes.end());
    }
    loc.x.binned_start = loc.x.start / bin_size * bin_size;
    loc.x.binned_end = full_bin
        ? ((loc.x.end + bin_size - 1) / bin_size * bin_size)
        : (loc.x.end / bin_size * bin_size);
    loc.y.binned_start = loc.y.start / bin_size * bin_size;
    loc.y.binned_end = full_bin
        ? ((loc.y.end + bin_size - 1) / bin_size * bin_size)
        : (loc.y.end / bin_size * bin_size);
    loc.x.bin_start = (loc.x.binned_start / bin_size);
    loc.x.bin_end = (loc.x.binned_end / bin_size);
    loc.y.bin_start = (loc.y.binned_start / bin_size);
    loc.y.bin_end = (loc.y.binned_end / bin_size);
    loc.bin_size = bin_size;
    return loc;
}
