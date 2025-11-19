struct ValueStats {
    f32 sum = 0;
    i64 count = 0;
};


struct FullValueStats {
    f32 min = std::numeric_limits<f32>::quiet_NaN();
    f32 max = std::numeric_limits<f32>::quiet_NaN();
    f32 sum = 0;
    f32 sum_squared = 0;
    i64 count = 0;
};


struct Loc {
    i64 chr_index;
    i64 start;
    i64 end;
    i64 binned_start;
    i64 binned_end;
    f64 bin_size;
    i64 output_start_index;
    i64 output_end_index;
};


class Locs : public std::vector<Loc> {
public:
    i64 bin_count;
    using std::vector<Loc>::vector;
};


struct LocsInterval {
    i64 start;
    i64 end;
};


class LocsIntervals : public std::vector<LocsInterval> {
public:
    using std::vector<LocsInterval>::vector;
};


Locs parse_locs(
    const OrderedMap<str, ChrItem>& chr_map,
    i64 key_size,
    const std::vector<str>& chr_ids,
    const std::vector<i64>& starts,
    const std::vector<i64>& ends,
    f64 bin_size = 1.0,
    i64 bin_count = -1,
    bool full_bin = false
) {
    if (chr_ids.size() != starts.size() || (!ends.empty() && chr_ids.size() != ends.size())) {
        throw std::runtime_error("length mismatch between chr_ids, starts or ends");
    }
    Locs locs(chr_ids.size());
    std::set<i64> binned_spans;
    for (i64 i = 0; i < static_cast<i64>(chr_ids.size()); ++i) {
        Loc loc;
        loc.chr_index = parse_chr(chr_ids[i], chr_map, key_size).index;
        loc.start = starts[i];
        loc.end = ends[i];
        if (loc.start > loc.end) {
            throw std::runtime_error(fstring("loc {}:{}-{} at index {} invalid", chr_ids[i], loc.start, loc.end, i));
        }
        loc.binned_start = static_cast<i64>(std::floor(loc.start / bin_size) * bin_size);
        loc.binned_end = full_bin
            ? static_cast<i64>(std::ceil(loc.end / bin_size) * bin_size)
            : static_cast<i64>(std::floor(loc.end / bin_size) * bin_size);
        locs[i] = loc;
        binned_spans.insert(loc.binned_end - loc.binned_start);
    }
    if (bin_count < 0) bin_count = static_cast<i64>(std::floor(*binned_spans.rbegin() / bin_size));
    std::sort(locs.begin(), locs.end(), [](const Loc& a, const Loc& b) {
        return std::tie(a.chr_index, a.binned_start, a.binned_end) < std::tie(b.chr_index, b.binned_start, b.binned_end);
    });
    for (i64 i = 0; i < static_cast<i64>(chr_ids.size()); ++i) {
        auto& loc = locs[i];
        loc.bin_size = static_cast<f64>(loc.binned_end - loc.binned_start) / bin_count;
        loc.output_start_index = i * bin_count;
        loc.output_end_index = loc.output_start_index + bin_count;
    }
    locs.bin_count = bin_count;
    return locs;
}


i64 get_locs_coverage(const Locs& locs) {
    i64 coverage = 0;
    for (const auto& loc : locs) {
        coverage += (loc.binned_end - loc.binned_start);
    }
    return coverage;
}


std::tuple<LocsIntervals, i64> get_locs_batchs(
    const Locs& locs,
    i64 parallel = 1
) {
    i64 total_coverage = get_locs_coverage(locs);
    i64 coverage_per_batch = total_coverage / parallel;
    LocsIntervals locs_batchs;
    if (locs.empty()) return {locs_batchs, 0};
    locs_batchs.push_back({0, 0});
    i64 coverage = 0;
    for (i64 i = 0 ; i < static_cast<i64>(locs.size()) - 1; ++i) {
        coverage += (locs[i].binned_end - locs[i].binned_start);
        if (coverage >= coverage_per_batch) {
            locs_batchs.back().end = i + 1;
            locs_batchs.push_back({i + 1, i + 1});
            coverage = 0;
        }
    }
    locs_batchs.back().end = locs.size();
    return {locs_batchs, total_coverage};
}
