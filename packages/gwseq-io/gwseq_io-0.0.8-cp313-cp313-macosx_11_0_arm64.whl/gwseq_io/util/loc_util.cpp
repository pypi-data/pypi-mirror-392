#include "includes.cpp"


struct ChrItem {
    str id;
    i64 index;
    i64 size;
};


std::tuple<std::vector<i64>, std::vector<i64>> preparse_locs(
    const std::vector<str>& chr_ids,
    const std::vector<i64>& starts={},
    const std::vector<i64>& ends={},
    const std::vector<i64>& centers={},
    i64 span = -1
) {
    std::vector<i64> preparsed_starts;
    std::vector<i64> preparsed_ends;
    if (span >= 0) {
        u8 starts_specified = starts.empty() ? 0 : 1;
        u8 ends_specified = ends.empty() ? 0 : 1;
        u8 centers_specified = centers.empty() ? 0 : 1;
        if (starts_specified + ends_specified + centers_specified != 1) {
            throw std::runtime_error("either starts/ends/centers must be specified when using span");
        } else if (starts_specified != 0) {
            preparsed_starts = starts;
            preparsed_ends.resize(starts.size());
            for (u64 i = 0; i < starts.size(); ++i) {
                preparsed_ends[i] = starts[i] + span;
            }
        } else if (ends_specified != 0) {
            preparsed_ends = ends;
            preparsed_starts.resize(ends.size());
            for (u64 i = 0; i < ends.size(); ++i) {
                preparsed_starts[i] = ends[i] - span;
            }
        } else {
            preparsed_starts.resize(centers.size());
            preparsed_ends.resize(centers.size());
            for (u64 i = 0; i < centers.size(); ++i) {
                preparsed_starts[i] = centers[i] - span / 2;
                preparsed_ends[i] = centers[i] + (span + 1) / 2;
            }
        }
    } else if (starts.empty() || ends.empty()) {
        throw std::runtime_error("either starts+ends or starts/ends/centers+span must be specified");
    } else {
        preparsed_starts = starts;
        preparsed_ends = ends;
    }
    if (chr_ids.size() != preparsed_starts.size() || chr_ids.size() != preparsed_ends.size()) {
        throw std::runtime_error("length mismatch between chr_ids and starts/ends/centers");
    }
    return {preparsed_starts, preparsed_ends};
}


ChrItem parse_chr(
    const str& chr_id,
    const OrderedMap<str, ChrItem>& chr_map,
    i64 key_size = -1
) {
    str chr_key = chr_id;
    if (key_size >= 0) chr_key = chr_key.substr(0, key_size);
    auto it = chr_map.find(chr_key);
    if (it != chr_map.end()) return it->second;
    it = chr_map.find(to_lowercase(chr_key));
    if (it != chr_map.end()) return it->second;
    it = chr_map.find(to_uppercase(chr_key));
    if (it != chr_map.end()) return it->second;
    if (to_lowercase(chr_id.substr(0, 3)) == "chr") {
        chr_key = chr_id.substr(3);
        if (key_size >= 0) chr_key = chr_key.substr(0, key_size);
    } else {
        chr_key = ("chr" + chr_id);
        if (key_size >= 0) chr_key = chr_key.substr(0, key_size);
    }
    it = chr_map.find(chr_key);
    if (it != chr_map.end()) return it->second;
    it = chr_map.find(to_lowercase(chr_key));
    if (it != chr_map.end()) return it->second;
    it = chr_map.find(to_uppercase(chr_key));
    if (it != chr_map.end()) return it->second;
    str available;
    for (const auto& entry : chr_map) {
        if (!available.empty()) available += ", ";
        available += entry.first;
    }
    throw std::runtime_error(fstring("chromosome {} missing ({})", chr_id, available));
}
