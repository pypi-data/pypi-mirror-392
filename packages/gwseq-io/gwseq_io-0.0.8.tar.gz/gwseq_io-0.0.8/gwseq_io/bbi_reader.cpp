class BBIReader {
    str path;
    i64 parallel;
    f64 zoom_correction;
    FilePool file_pool;

    std::tuple<Locs, LocsIntervals, i64, i64, std::shared_ptr<ProgressTracker>> init_extraction(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        f64 bin_size = 1.0,
        i64 bin_count = -1,
        bool full_bin = false,
        i64 zoom = -1,
        std::function<void(i64, i64)> progress = nullptr
    ) {
        auto [preparsed_starts, preparsed_ends] = preparse_locs(chr_ids, starts, ends, centers, span);
        auto locs = parse_locs(chr_map, chr_tree_header.key_size, chr_ids, preparsed_starts, preparsed_ends, bin_size, bin_count, full_bin);
        auto [locs_batchs, coverage] = get_locs_batchs(locs, parallel);
        auto zoom_level = select_zoom_level(bin_size, zoom);
        i64 data_tree_offset = (zoom_level < 0) ? bbi_header.full_index_offset + 48 : zoom_headers[zoom_level].index_offset + 48;
        auto tracker = std::make_shared<ProgressTracker>(coverage, progress);
        return {locs, locs_batchs, zoom_level, data_tree_offset, tracker};
    }

    std::vector<f32> signal_extraction(
        const Locs& locs,
        const LocsIntervals& locs_batchs,
        i64 zoom_level,
        i64 data_tree_offset,
        ProgressTracker* tracker,
        const str& bin_mode,
        f32 def_value
    ) {
        ThreadPool thread_pool(parallel);
        i64 output_size = locs.empty() ? 0 : locs.back().output_end_index;
        std::vector<ValueStats> output_stats(output_size);
        for (const auto& locs_interval : locs_batchs) {
            thread_pool.enqueue([this, &locs, locs_interval, zoom_level, data_tree_offset, tracker, &output_stats] {
                auto file = file_pool.get_pseudo_file();
                DataTreeGenerator data_tree_items(file, locs, locs_interval, *tracker, data_tree_offset);
                for (const auto& [tree_item, item_locs_interval] : data_tree_items) {
                    DataIntervalGenerator data_intervals(file, tree_item, locs, item_locs_interval, zoom_level, bbi_header.uncompress_buffer_size);
                    for (const auto& interval : data_intervals) {
                        for (i64 loc_index = item_locs_interval.start; loc_index < item_locs_interval.end; ++loc_index) {
                            const Loc& loc = locs[loc_index];
                            if (interval.start >= loc.binned_end) continue;
                            if (interval.end <= loc.binned_start) break;
                            i64 overlap_start = std::max(interval.start, loc.binned_start);
                            i64 overlap_end = std::min(interval.end, loc.binned_end);
                            i64 loc_bin_start = static_cast<i64>(std::floor(loc.binned_start / loc.bin_size));
                            i64 bin_start = static_cast<i64>(std::floor(overlap_start / loc.bin_size));
                            i64 bin_end = static_cast<i64>(std::ceil(overlap_end / loc.bin_size));
                            for (i64 b = bin_start; b < bin_end; b += 1) {
                                i64 output_index = loc.output_start_index + (b - loc_bin_start);
                                if (output_index >= loc.output_end_index) break;
                                ValueStats& value_stats = output_stats[output_index];
                                value_stats.sum += interval.value;
                                value_stats.count += 1;
                            }
                        }
                    }
                }
            });
        }
        thread_pool.wait();
        tracker->done();
        std::vector<f32> output(output_size, def_value);
        for (i64 i = 0; i < output_size; ++i) {
            const ValueStats& value_stats = output_stats[i];
            if (value_stats.count == 0) continue;
            if (bin_mode == "mean") {
                output[i] = value_stats.sum / static_cast<f32>(value_stats.count);
            } else if (bin_mode == "sum") {
                output[i] = value_stats.sum;
            } else if (bin_mode == "count") {
                output[i] = static_cast<f32>(value_stats.count);
            } else {
                throw std::runtime_error(fstring("bin_mode {} invalid", bin_mode));
            }
        }
        return output;
    }

    std::vector<FullValueStats> signal_stats_extraction(
        const Locs& locs,
        const LocsIntervals& locs_batchs,
        i64 zoom_level,
        i64 data_tree_offset,
        ProgressTracker* tracker
    ) {
        ThreadPool thread_pool(parallel);
        std::vector<FullValueStats> output_stats(locs.size());
        for (const auto& locs_interval : locs_batchs) {
            thread_pool.enqueue([this, &locs, locs_interval, zoom_level, data_tree_offset, tracker, &output_stats] {
                auto file = file_pool.get_pseudo_file();
                DataTreeGenerator data_tree_items(file, locs, locs_interval, *tracker, data_tree_offset);
                for (const auto& [tree_item, item_locs_interval] : data_tree_items) {
                    DataIntervalGenerator data_intervals(file, tree_item, locs, item_locs_interval, zoom_level, bbi_header.uncompress_buffer_size);
                    for (const auto& interval : data_intervals) {
                        for (i64 loc_index = item_locs_interval.start; loc_index < item_locs_interval.end; ++loc_index) {
                            const Loc& loc = locs[loc_index];
                            if (interval.start >= loc.binned_end) continue;
                            if (interval.end <= loc.binned_start) break;
                            i64 overlap_start = std::max(interval.start, loc.binned_start);
                            i64 overlap_end = std::min(interval.end, loc.binned_end);
                            i64 overlap = overlap_end - overlap_start;
                            FullValueStats& value_stats = output_stats[loc_index];
                            if (interval.value < value_stats.min || std::isnan(value_stats.min)) value_stats.min = interval.value;
                            if (interval.value > value_stats.max || std::isnan(value_stats.max)) value_stats.max = interval.value;
                            value_stats.sum += interval.value * overlap;
                            value_stats.sum_squared += interval.value * interval.value * overlap;
                            value_stats.count += overlap;
                        }
                    }
                }
            });
        }
        thread_pool.wait();
        tracker->done();
        return output_stats;
    }


    std::vector<FullValueStats> signal_profile_extraction(
        const Locs& locs,
        const LocsIntervals& locs_batchs,
        i64 zoom_level,
        i64 data_tree_offset,
        ProgressTracker* tracker
    ) {
        ThreadPool thread_pool(parallel);
        std::vector<std::vector<FullValueStats>> batchs_output_stats(locs_batchs.size());
        for (size_t batch_index = 0; batch_index < locs_batchs.size(); ++batch_index) {
            thread_pool.enqueue([this, &locs, locs_interval = locs_batchs[batch_index], zoom_level, data_tree_offset, tracker, &batchs_output_stats, batch_index] {
                auto file = file_pool.get_pseudo_file();
                std::vector<FullValueStats> batch_output_stats(locs.bin_count);
                DataTreeGenerator data_tree_items(file, locs, locs_interval, *tracker, data_tree_offset);
                for (const auto& [tree_item, item_locs_interval] : data_tree_items) {
                    DataIntervalGenerator data_intervals(file, tree_item, locs, item_locs_interval, zoom_level, bbi_header.uncompress_buffer_size);
                    for (const auto& interval : data_intervals) {
                        for (i64 loc_index = item_locs_interval.start; loc_index < item_locs_interval.end; ++loc_index) {
                            const Loc& loc = locs[loc_index];
                            if (interval.start >= loc.binned_end) continue;
                            if (interval.end <= loc.binned_start) break;
                            i64 overlap_start = std::max(interval.start, loc.binned_start);
                            i64 overlap_end = std::min(interval.end, loc.binned_end);
                            i64 loc_bin_start = static_cast<i64>(std::floor(loc.binned_start / loc.bin_size));
                            i64 bin_start = static_cast<i64>(std::floor(overlap_start / loc.bin_size));
                            i64 bin_end = static_cast<i64>(std::ceil(overlap_end / loc.bin_size));
                            for (i64 b = bin_start; b < bin_end; b += 1) {
                                i64 output_index = b - loc_bin_start;
                                if (output_index >= locs.bin_count) continue;
                                FullValueStats& value_stats = batch_output_stats[output_index];
                                if (interval.value < value_stats.min || std::isnan(value_stats.min)) value_stats.min = interval.value;
                                if (interval.value > value_stats.max || std::isnan(value_stats.max)) value_stats.max = interval.value;
                                value_stats.sum += interval.value;
                                value_stats.sum_squared += interval.value * interval.value;
                                value_stats.count += 1;
                            }
                        }
                    }
                }
                batchs_output_stats[batch_index] = std::move(batch_output_stats);
            });
        }
        thread_pool.wait();
        tracker->done();
        std::vector<FullValueStats> output_stats(locs.bin_count);
        for (i64 col = 0; col < locs.bin_count; ++col) {
            FullValueStats& value_stats = output_stats[col];
            for (const auto& batch_output_stats : batchs_output_stats) {
                const FullValueStats& batch_value_stats = batch_output_stats[col];
                if (batch_value_stats.count == 0) continue;
                if (batch_value_stats.min < value_stats.min || std::isnan(value_stats.min)) value_stats.min = batch_value_stats.min;
                if (batch_value_stats.max > value_stats.max || std::isnan(value_stats.max)) value_stats.max = batch_value_stats.max;
                value_stats.sum += batch_value_stats.sum;
                value_stats.sum_squared += batch_value_stats.sum_squared;
                value_stats.count += batch_value_stats.count;
            }
        }
        return output_stats;
    }

    std::vector<std::vector<BedEntry>> entries_extraction(
        const Locs& locs,
        const LocsIntervals& locs_batchs,
        i64 data_tree_offset,
        ProgressTracker* tracker
    ) {
        ThreadPool thread_pool(parallel);
        std::vector<std::vector<BedEntry>> output(locs.size());
        for (const auto& locs_interval : locs_batchs) {
            thread_pool.enqueue([this, &locs, locs_interval, data_tree_offset, tracker, &output] {
                auto file = file_pool.get_pseudo_file();
                DataTreeGenerator data_tree_items(file, locs, locs_interval, *tracker, data_tree_offset);
                for (const auto& [tree_item, item_locs_interval] : data_tree_items) {
                    BedEntryGenerator bed_entries(file, tree_item, locs, item_locs_interval, auto_sql, bbi_header.uncompress_buffer_size);
                    for (const auto& entry : bed_entries) {
                        for (i64 loc_index = locs_interval.start; loc_index < locs_interval.end; ++loc_index) {
                            const Loc& loc = locs[loc_index];
                            if (entry.chr_index != loc.chr_index) continue;
                            if (entry.start >= loc.binned_end) continue;
                            if (entry.end <= loc.binned_start) break;
                            output[loc_index].push_back(entry);
                        }
                    }
                }
            });
        }
        thread_pool.wait();
        tracker->done();
        for (auto& entries : output) {
            std::sort(entries.begin(), entries.end(), [](const BedEntry& a, const BedEntry& b) {
                return std::tie(a.chr_index, a.start, a.end) < std::tie(b.chr_index, b.start, b.end);
            });
        }
        return output;
    }

    std::vector<f32> entries_pileup(
        const Locs& locs,
        const LocsIntervals& locs_batchs,
        i64 zoom_level,
        i64 data_tree_offset,
        ProgressTracker* tracker
    ) {
        ThreadPool thread_pool(parallel);
        i64 output_size = locs.empty() ? 0 : locs.back().output_end_index;
        std::vector<f32> output(output_size, 0.0);
        for (const auto& locs_interval : locs_batchs) {
            thread_pool.enqueue([this, &locs, locs_interval, data_tree_offset, tracker, &output] {
                auto file = file_pool.get_pseudo_file();
                DataTreeGenerator data_tree_items(file, locs, locs_interval, *tracker, data_tree_offset);
                for (const auto& [tree_item, item_locs_interval] : data_tree_items) {
                    BedEntryGenerator bed_entries(file, tree_item, locs, item_locs_interval, auto_sql, bbi_header.uncompress_buffer_size);
                    for (const auto& entry : bed_entries) {
                        for (i64 loc_index = locs_interval.start; loc_index < locs_interval.end; ++loc_index) {
                            const Loc& loc = locs[loc_index];
                            if (entry.chr_index != loc.chr_index) continue;
                            if (entry.start >= loc.binned_end) continue;
                            if (entry.end <= loc.binned_start) break;
                            i64 overlap_start = std::max(entry.start, loc.binned_start);
                            i64 overlap_end = std::min(entry.end, loc.binned_end);
                            i64 loc_bin_start = static_cast<i64>(std::floor(loc.binned_start / loc.bin_size));
                            i64 bin_start = static_cast<i64>(std::floor(overlap_start / loc.bin_size));
                            i64 bin_end = static_cast<i64>(std::ceil(overlap_end / loc.bin_size));
                            for (i64 b = bin_start; b < bin_end; b += 1) {
                                i64 output_index = loc.output_start_index + (b - loc_bin_start);
                                if (output_index >= loc.output_end_index) break;
                                output[output_index] += 1.0;
                            }
                        }
                    }
                }
            });
        }
        thread_pool.wait();
        tracker->done();
        return output;
    }

    std::vector<FullValueStats> entries_pileup_stats(
        const Locs& locs,
        const LocsIntervals& locs_batchs,
        i64 zoom_level,
        i64 data_tree_offset,
        ProgressTracker* tracker
    ) {
        auto pileup = entries_pileup(locs, locs_batchs, zoom_level, data_tree_offset, tracker);
        std::vector<FullValueStats> output_stats(locs.size());
        for (u64 row = 0; row < locs.size(); ++row) {
            Loc loc = locs[row];
            FullValueStats& value_stats = output_stats[row];
            for (i64 i = loc.output_start_index; i < loc.output_end_index; ++i) {
                f32 value = pileup[i];
                if (value < value_stats.min || std::isnan(value_stats.min)) value_stats.min = value;
                if (value > value_stats.max || std::isnan(value_stats.max)) value_stats.max = value;
                value_stats.sum += value;
                value_stats.sum_squared += value * value;
                value_stats.count += value > 0 ? 1 : 0;
            }
        }
        return output_stats;
    }

    std::vector<FullValueStats> entries_pileup_profile(
        const Locs& locs,
        const LocsIntervals& locs_batchs,
        i64 zoom_level,
        i64 data_tree_offset,
        ProgressTracker* tracker
    ) {
        auto pileup = entries_pileup(locs, locs_batchs, zoom_level, data_tree_offset, tracker);
        std::vector<FullValueStats> output_stats(locs.bin_count);
        for (i64 col = 0; col < locs.bin_count; ++col) {
            FullValueStats& value_stats = output_stats[col];
            for (i64 row = 0; row < static_cast<i64>(locs.size()); ++row) {
                f32 value = pileup[row * locs.bin_count + col];
                if (value < value_stats.min || std::isnan(value_stats.min)) value_stats.min = value;
                if (value > value_stats.max || std::isnan(value_stats.max)) value_stats.max = value;
                value_stats.sum += value;
                value_stats.sum_squared += value * value;
                value_stats.count += value > 0 ? 1 : 0;
            }
        }
        return output_stats;
    }

    std::vector<f32> reduce_output_stats(
        const std::vector<FullValueStats>& output_stats,
        const str& reduce,
        f32 def_value
    ) {
        std::vector<f32> output(output_stats.size(), def_value);
        for (u64 i = 0; i < output_stats.size(); ++i) {
            const FullValueStats& value_stats = output_stats[i];
            if (value_stats.count == 0) continue;
            if (reduce == "mean") {
                output[i] = value_stats.sum / value_stats.count;
            } else if (reduce == "sd") {
                f32 mean = value_stats.sum / value_stats.count;
                f32 variance = (value_stats.sum_squared / value_stats.count) - (mean * mean);
                output[i] = std::sqrt(variance);
            } else if (reduce == "sem") {
                f32 mean = value_stats.sum / value_stats.count;
                f32 variance = (value_stats.sum_squared / value_stats.count) - (mean * mean);
                output[i] = std::sqrt(variance) / std::sqrt(static_cast<f32>(value_stats.count));
            } else if (reduce == "sum") {
                output[i] = value_stats.sum;
            } else if (reduce == "count") {
                output[i] = value_stats.count;
            } else if (reduce == "min") {
                output[i] = value_stats.min;
            } else if (reduce == "max") {
                output[i] = value_stats.max;
            } else {
                throw std::runtime_error("reduce " + reduce + " invalid");
            }
        }
        return output;
    }

public:
    BBIHeader bbi_header;
    std::vector<ZoomHeader> zoom_headers;
    OrderedMap<str, str> auto_sql;
    TotalSummary total_summary;
    ChrTreeHeader chr_tree_header;
    std::vector<ChrItem> chr_list;
    OrderedMap<str, ChrItem> chr_map;
    str type;
    i64 data_count;

    BBIReader(
        const str& path,
        i64 parallel = 24,
        f64 zoom_correction = 1.0/3.0,
        i64 file_buffer_size = 32768,
        i64 max_file_buffer_count = 128
    ) : path(path), parallel(parallel), zoom_correction(zoom_correction),
        file_pool(path, "r", parallel, file_buffer_size, max_file_buffer_count)
    {
        auto file = file_pool.get_pseudo_file();
        bbi_header = read_bbi_header(file);
        zoom_headers = read_zoom_headers(file, bbi_header.zoom_levels);
        auto_sql = read_auto_sql(file, bbi_header.auto_sql_offset, bbi_header.field_count);
        total_summary = read_total_summary(file, bbi_header.total_summary_offset);
        chr_tree_header = read_chr_tree_header(file, bbi_header.chr_tree_offset);
        chr_list = read_chr_list(file, bbi_header.chr_tree_offset + 32, chr_tree_header.key_size);
        chr_map = OrderedMap<str, ChrItem>();
        for (const auto& item : chr_list) {
            chr_map.insert(item.id, item);
        }
        type = (bbi_header.magic == BIGWIG_MAGIC) ? "bigwig" : "bigbed";
        data_count = static_cast<i64>(file.read(4, bbi_header.full_data_offset).read<u32>(0));
    }

    i64 select_zoom_level(f64 bin_size, i64 request = -1) {
        i64 zoom_count = static_cast<i64>(zoom_headers.size());
        if (request >= -1) {
            if (request < zoom_count) return request;
            throw std::runtime_error(fstring("requested zoom level {} exceeds max zoom level {}", request, zoom_headers.size() - 1));
        }
        i64 best_level = -1;
        i64 best_reduction = 0;
        i64 rounded_bin_size = static_cast<i64>(std::round(bin_size * zoom_correction));
        for (i64 i = 0; i < zoom_count; ++i) {
            i64 reduction = zoom_headers[i].reduction_level;
            if (reduction <= rounded_bin_size && reduction > best_reduction) {
                best_reduction = reduction;
                best_level = i;
            }
        }
        return best_level;
    }

    std::vector<f32> read_signal(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        f64 bin_size = 1.0,
        i64 bin_count = -1,
        str bin_mode = "mean",
        bool full_bin = false,
        f32 def_value = 0.0f,
        i64 zoom = -1,
        std::function<void(i64, i64)> progress = nullptr
    ) {
        auto [locs, locs_batchs, zoom_level, data_tree_offset, tracker] = init_extraction(chr_ids, starts, ends, centers, span, bin_size, bin_count, full_bin, zoom, progress);

        if (type == "bigbed") return entries_pileup(locs, locs_batchs, zoom_level, data_tree_offset, tracker.get());
        return signal_extraction(locs, locs_batchs, zoom_level, data_tree_offset, tracker.get(), bin_mode, def_value);
    }

    std::vector<f32> quantify(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        f64 bin_size = 1.0,
        bool full_bin = false,
        f32 def_value = 0.0f,
        str reduce = "mean",
        i64 zoom = -1,
        std::function<void(i64, i64)> progress = nullptr
    ) {
        auto [locs, locs_batchs, zoom_level, data_tree_offset, tracker] = init_extraction(chr_ids, starts, ends, centers, span, bin_size, 1, full_bin, zoom, progress);

        auto output_stats = (type == "bigbed")
            ? entries_pileup_stats(locs, locs_batchs, zoom_level, data_tree_offset, tracker.get())
            : signal_stats_extraction(locs, locs_batchs, zoom_level, data_tree_offset, tracker.get());
        return reduce_output_stats(output_stats, reduce, def_value);
    }

    std::vector<f32> profile(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        f64 bin_size = 1.0,
        i64 bin_count = -1,
        str bin_mode = "mean",
        bool full_bin = false,
        f32 def_value = 0.0f,
        str reduce = "mean",
        i64 zoom = -1,
        std::function<void(i64, i64)> progress = nullptr
    ) {
        auto [locs, locs_batchs, zoom_level, data_tree_offset, tracker] = init_extraction(chr_ids, starts, ends, centers, span, bin_size, bin_count, full_bin, zoom, progress);
        
        auto output_stats = (type == "bigbed")
            ? entries_pileup_profile(locs, locs_batchs, zoom_level, data_tree_offset, tracker.get())
            : signal_profile_extraction(locs, locs_batchs, zoom_level, data_tree_offset, tracker.get());
        return reduce_output_stats(output_stats, reduce, def_value);
    }

    std::vector<std::vector<BedEntry>> read_entries(
        const std::vector<str>& chr_ids = {},
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        f64 bin_size = 1.0,
        bool full_bin = false,
        std::function<void(i64, i64)> progress = nullptr
    ) {
        if (type != "bigbed") throw std::runtime_error("read_entries only for bigbed");
        auto [locs, locs_batchs, __zoom_level, data_tree_offset, tracker] = init_extraction(chr_ids, starts, ends, centers, span, bin_size, 1, full_bin, -1, progress);

        return entries_extraction(locs, locs_batchs, data_tree_offset, tracker.get());
    }

    void to_bedgraph(
        const str& output_path,
        const std::vector<str>& chr_ids = {},
        f64 bin_size = 1.0,
        i64 zoom = -1,
        std::function<void(i64, i64)> progress = nullptr
    ) {
        if (type != "bigwig") throw std::runtime_error("to_bedgraph only for bigwig");

        std::vector<i64> starts, ends;
        for (auto chr_id : (chr_ids.empty() ? chr_map.keys() : chr_ids)) {
            starts.push_back(0);
            ends.push_back(parse_chr(chr_id, chr_map, chr_tree_header.key_size).size);
        }
        auto [locs, locs_batchs, zoom_level, data_tree_offset, tracker] = init_extraction(chr_ids, starts, ends, {}, -1, bin_size, 1, false, zoom, progress);

        auto output_file = open_file(output_path, "w");
        auto write_line = [&](str chr_id, u32 start, u32 end, f32 value) {
            str line =
                chr_id + "\t" +
                std::to_string(start) + "\t" +
                std::to_string(end) + "\t" +
                std::to_string(value) + "\n";
            output_file->write_string(line);
        };
        auto file = file_pool.get_pseudo_file();
        for (const auto& locs_interval : locs_batchs) {
            DataTreeGenerator data_tree_items(file, locs, locs_interval, *tracker, data_tree_offset);
            for (const auto& [tree_item, item_locs_interval] : data_tree_items) {
                DataIntervalGenerator data_intervals(file, tree_item, locs, item_locs_interval, zoom_level, bbi_header.uncompress_buffer_size);
                for (const auto& interval : data_intervals) {
                    str chr_id = chr_list[interval.chr_index].id;
                    write_line(chr_id, interval.start, interval.end, interval.value);
                }
            }
        }
        tracker->done();
    }

    void to_wig(
        const str& output_path,
        const std::vector<str>& chr_ids = {},
        f64 bin_size = 1.0,
        i64 zoom = -1,
        std::function<void(i64, i64)> progress = nullptr
    ) {
        if (type != "bigwig") throw std::runtime_error("to_bedgraph only for bigwig");

        std::vector<i64> starts, ends;
        for (auto chr_id : (chr_ids.empty() ? chr_map.keys() : chr_ids)) {
            starts.push_back(0);
            ends.push_back(parse_chr(chr_id, chr_map, chr_tree_header.key_size).size);
        }
        auto [locs, locs_batchs, zoom_level, data_tree_offset, tracker] = init_extraction(chr_ids, starts, ends, {}, -1, bin_size, 1, false, zoom, progress);

        auto output_file = open_file(output_path, "w");
        auto write_header_line = [&](str chr_id, u32 start, i64 span) {
            str line =
                "fixedStep chrom=" + chr_id +
                " start=" + std::to_string(start + 1) +
                " step=" + std::to_string(span) +
                " span=" + std::to_string(span) + "\n";
            output_file->write_string(line);
        };
        auto file = file_pool.get_pseudo_file();
        for (const auto& locs_interval : locs_batchs) {
            DataTreeGenerator data_tree_items(file, locs, locs_interval, *tracker, data_tree_offset);
            for (const auto& [tree_item, item_locs_interval] : data_tree_items) {
                DataIntervalGenerator data_intervals(file, tree_item, locs, item_locs_interval, zoom_level, bbi_header.uncompress_buffer_size);
                i64 span = -1;
                for (const auto& interval : data_intervals) {
                    str chr_id = chr_list[interval.chr_index].id;
                    if (interval.end - interval.start != span) {
                        span = interval.end - interval.start;
                        write_header_line(chr_id, interval.start, span);
                    }
                    output_file->write_string(std::to_string(interval.value) + "\n");
                }
            }
        }
        tracker->done();
    }

    void to_bed(
        const str& output_path,
        const std::vector<str>& chr_ids = {},
        i64 col_count = 0,
        std::function<void(i64, i64)> progress = nullptr
    ) {
        if (type != "bigbed") throw std::runtime_error("to_bed only for bigbed");
        if (col_count == 0) col_count = bbi_header.field_count;
        if (col_count > bbi_header.field_count) {
            throw std::runtime_error(fstring("col_count {} exceeds number of fields {}", col_count, bbi_header.field_count));
        }

        std::vector<i64> starts, ends;
        for (auto chr_id : (chr_ids.empty() ? chr_map.keys() : chr_ids)) {
            starts.push_back(0);
            ends.push_back(parse_chr(chr_id, chr_map, chr_tree_header.key_size).size);
        }
        auto [locs, locs_batchs, __zoom_level, data_tree_offset, tracker] = init_extraction(chr_ids, starts, ends, {}, -1, 1, 1, false, -1, progress);

        auto output_file = open_file(output_path, "w");
        auto file = file_pool.get_pseudo_file();
        for (const auto& locs_interval : locs_batchs) {
            DataTreeGenerator data_tree_items(file, locs, locs_interval, *tracker, data_tree_offset);
            for (const auto& [tree_item, item_locs_interval] : data_tree_items) {
                BedEntryGenerator bed_entries(file, tree_item, locs, item_locs_interval, auto_sql, bbi_header.uncompress_buffer_size);
                for (const auto& entry : bed_entries) {
                    str chr_id = chr_list[entry.chr_index].id;
                    str line =
                        col_count == 1 ? chr_id :
                        col_count == 2 ? chr_id + "\t" + std::to_string(entry.start) :
                        chr_id + "\t" + std::to_string(entry.start) + "\t" + std::to_string(entry.end);
                    i64 col_index = 3;
                    for (const auto& field : entry.fields) {
                        if (col_index >= col_count) break;
                        line += "\t" + field.second;
                        col_index += 1;
                    }
                    line += "\n";
                    output_file->write_string(line);
                }
            }
        }
        tracker->done();
    }
};
