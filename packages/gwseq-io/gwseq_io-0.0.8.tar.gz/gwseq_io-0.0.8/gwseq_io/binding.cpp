#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "main.cpp"

namespace py = pybind11;


py::dict py_get_chr_sizes(const str& genome) {
    auto chr_sizes = get_genome_chr_sizes(genome);
    py::dict result;
    for (const auto& pair : chr_sizes) {
        result[py::cast(pair.first)] = py::cast(pair.second);
    }
    return result;
}


std::function<void(i64, i64)> py_init_progress_callback(py::object progress) {
    if (progress.is_none()) return nullptr;
    if (py::isinstance<py::bool_>(progress)) {
        if (progress.cast<bool>()) {
            auto callback = std::make_shared<ProgressCallback>();
            return [callback](i64 current, i64 total) {
                (*callback)(current, total);
            };
        }
        return nullptr;
    }
    return [progress](i64 current, i64 total) {
        py::gil_scoped_acquire acquire;
        try {
            progress(current, total);
        } catch (const py::error_already_set& e) {
            // ignore error in python callback
        }
    };
}


class PyBBIReader {
    BBIReader reader;

public:
    py::dict bbi_header;
    py::list zoom_headers;
    py::dict auto_sql;
    py::dict total_summary;
    py::dict chr_tree_header;
    py::dict chr_sizes;
    str type;
    i64 data_count;
    
    PyBBIReader(
        const str& path,
        i64 parallel = 24,
        f64 zoom_correction = 1.0/3.0,
        i64 file_buffer_size = 32768,
        i64 max_file_buffer_count = 128
    ) : reader(path, parallel, zoom_correction, file_buffer_size, max_file_buffer_count) {

        bbi_header["magic"] = reader.bbi_header.magic;
        bbi_header["version"] = reader.bbi_header.version;
        bbi_header["zoom_levels"] = reader.bbi_header.zoom_levels;
        bbi_header["chr_tree_offset"] = reader.bbi_header.chr_tree_offset;
        bbi_header["full_data_offset"] = reader.bbi_header.full_data_offset;
        bbi_header["full_index_offset"] = reader.bbi_header.full_index_offset;
        bbi_header["field_count"] = reader.bbi_header.field_count;
        bbi_header["defined_field_count"] = reader.bbi_header.defined_field_count;
        bbi_header["auto_sql_offset"] = reader.bbi_header.auto_sql_offset;
        bbi_header["total_summary_offset"] = reader.bbi_header.total_summary_offset;
        bbi_header["uncompress_buffer_size"] = reader.bbi_header.uncompress_buffer_size;
        // bbi_header["reserved"] = reader.bbi_header.reserved;

        for (const auto& field : reader.auto_sql) {
            auto_sql[py::str(field.first)] = field.second;
        }

        total_summary["bases_covered"] = reader.total_summary.bases_covered;
        total_summary["min_value"] = reader.total_summary.min_value;
        total_summary["max_value"] = reader.total_summary.max_value;
        total_summary["sum_data"] = reader.total_summary.sum_data;
        total_summary["sum_squared"] = reader.total_summary.sum_squared;

        chr_tree_header["magic"] = reader.chr_tree_header.magic;
        chr_tree_header["block_size"] = reader.chr_tree_header.block_size;
        chr_tree_header["key_size"] = reader.chr_tree_header.key_size;
        chr_tree_header["value_size"] = reader.chr_tree_header.value_size;
        chr_tree_header["item_count"] = reader.chr_tree_header.item_count;
        // chr_tree_header["reserved"] = reader.chr_tree_header.reserved;

        for (const auto& zoom_header : reader.zoom_headers) {
            py::dict zoom_header_dict;
            zoom_header_dict["reduction_level"] = zoom_header.reduction_level;
            // zoom_header_dict["reserved"] = zoom_header.reserved;
            zoom_header_dict["data_offset"] = zoom_header.data_offset;
            zoom_header_dict["index_offset"] = zoom_header.index_offset;
            zoom_headers.append(zoom_header_dict);
        }

        for (const auto& chr : reader.chr_map) {
            chr_sizes[py::str(chr.first)] = chr.second.size;
        }

        type = reader.type;
        data_count = reader.data_count;
    }

    py::list py_parse_locs(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        f64 bin_size = 1.0,
        i64 bin_count = -1,
        bool full_bin = false
    ) {
        auto [preparsed_starts, preparsed_ends] = preparse_locs(chr_ids, starts, ends, centers, span);
        auto locs = parse_locs(reader.chr_map, reader.chr_tree_header.key_size, chr_ids, preparsed_starts, preparsed_ends, bin_size, bin_count, full_bin);
        py::list py_locs;
        for (const auto& loc : locs) {
            auto chr_size = reader.chr_list[loc.chr_index].size;
            py::dict py_loc;
            py_loc["chr_id"] = reader.chr_list[loc.chr_index].id;
            py_loc["chr_index"] = loc.chr_index;
            py_loc["start"] = loc.start;
            py_loc["end"] = loc.end;
            py_loc["binned_start"] = loc.binned_start;
            py_loc["binned_end"] = loc.binned_end;
            py_loc["bin_size"] = loc.bin_size;
            py_loc["bin_count"] = locs.bin_count;
            py_loc["output_start_index"] = loc.output_start_index;
            py_loc["output_end_index"] = loc.output_end_index;
            py_loc["chr_bounds"] = py::dict(
                py::arg("start")=std::make_tuple(loc.start, loc.start - chr_size),
                py::arg("end")=std::make_tuple(loc.end, loc.end - chr_size),
                py::arg("binned_start")=std::make_tuple(loc.binned_start, loc.binned_start - chr_size),
                py::arg("binned_end")=std::make_tuple(loc.binned_end, loc.binned_end - chr_size)
            );
            py_locs.append(py_loc);
        }
        return py_locs;
    }

    py::array_t<f32> py_read_signal(
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
        py::object progress = py::none()
    ) {
        auto progress_callback = py_init_progress_callback(progress);
        std::vector<f32> values;
        {
            py::gil_scoped_release release;
            values = reader.read_signal(
                chr_ids, starts, ends, centers, span,
                bin_size, bin_count, bin_mode, full_bin,
                def_value, zoom, progress_callback
            );
        }
        size_t row_count = chr_ids.size();
        size_t col_count = values.size() / row_count;
        std::vector<size_t> shape = {row_count, col_count};
        std::vector<size_t> strides = {col_count * sizeof(f32), sizeof(f32)};
        return py::array_t<f32>(shape, strides, values.data());
    }

    py::array_t<f32> py_quantify(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        f64 bin_size = 1,
        bool full_bin = false,
        f32 def_value = 0.0f,
        str reduce = "mean",
        i64 zoom = -1,
        py::object progress = py::none()
    ) {
        auto progress_callback = py_init_progress_callback(progress);
        std::vector<f32> values;
        {
            py::gil_scoped_release release;
            values = reader.quantify(
                chr_ids, starts, ends, centers, span,
                bin_size, full_bin,
                def_value, reduce, zoom, progress_callback
            );
        }
        std::vector<size_t> shape = {values.size()};
        std::vector<size_t> strides = {sizeof(f32)};
        return py::array_t<f32>(shape, strides, values.data());
    }

    py::array_t<f32> py_profile(
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
        py::object progress = py::none()
    ) {
        auto progress_callback = py_init_progress_callback(progress);
        std::vector<f32> values;
        {
            py::gil_scoped_release release;
            values = reader.profile(
                chr_ids, starts, ends, centers, span,
                bin_size, bin_count, bin_mode, full_bin,
                def_value, reduce, zoom, progress_callback
            );
        }
        std::vector<size_t> shape = {values.size()};
        std::vector<size_t> strides = {sizeof(f32)};
        return py::array_t<f32>(shape, strides, values.data());
    }

    py::list py_read_entries(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        f64 bin_size = 1.0,
        bool full_bin = false,
        py::object progress = py::none()
    ) {
        auto progress_callback = py_init_progress_callback(progress);
        std::vector<std::vector<BedEntry>> locs_entries;
        {
            py::gil_scoped_release release;
            locs_entries = reader.read_entries(
                chr_ids, starts, ends, centers, span,
                bin_size, full_bin, progress_callback
            );
        }
        py::list py_locs_entries;
        for (const auto& entries : locs_entries) {
            py::list py_entries;
            for (const auto& entry : entries) {
                py::dict py_entry;
                py_entry["chr"] = reader.chr_list[entry.chr_index].id;
                py_entry["start"] = entry.start;
                py_entry["end"] = entry.end;
                for (const auto& field : entry.fields) {
                    py_entry[py::str(field.first)] = field.second;
                }
                py_entries.append(py_entry);
            }
            py_locs_entries.append(py_entries);
        }
        return py_locs_entries;
    }

    void py_to_bedgraph(
        const str& output_path,
        std::vector<str> chr_ids = {},
        f64 bin_size = 1.0,
        i64 zoom = -1,
        py::object progress = py::none()
    ) {
        auto progress_callback = py_init_progress_callback(progress);
        py::gil_scoped_release release;
        reader.to_bedgraph(output_path, chr_ids, bin_size, zoom, progress_callback);
    }
    
    void py_to_wig(
        const str& output_path,
        std::vector<str> chr_ids = {},
        f64 bin_size = 1.0,
        i64 zoom = -1,
        py::object progress = py::none()
    ) {
        auto progress_callback = py_init_progress_callback(progress);
        py::gil_scoped_release release;
        reader.to_wig(output_path, chr_ids, bin_size, zoom, progress_callback);
    }

    void py_to_bed(
        const str& output_path,
        std::vector<str> chr_ids = {},
        i64 col_count = 0,
        py::object progress = py::none()
    ) {
        auto progress_callback = py_init_progress_callback(progress);
        py::gil_scoped_release release;
        reader.to_bed(output_path, chr_ids, col_count, progress_callback);
    }
};


class PyBBIWriter {
public:
    PyBBIWriter(
        const str& path,
        const str& type = "bigwig"
    ) {
        throw std::runtime_error("Writer not yet implemented");
    }
};


class PyBAMReader {
    BAMReader reader;

public:
    py::list header;
    py::dict chr_map;

    PyBAMReader(
        const str& path,
        i64 parallel = 24,
        i64 file_buffer_size = 32768,
        i64 max_file_buffer_count = 128,
        str index_path = ""
    ) : reader(path, parallel, file_buffer_size, max_file_buffer_count, index_path) {
        for (const auto& line : reader.header.lines) {
            py::dict py_line;
            py_line["type"] = line.type;
            py_line["fields"] = py::dict();
            for (const auto& field : line.fields) {
                py_line["fields"][py::str(field.tag)] = field.value;
            }
            header.append(py_line);
        }
        for (const auto& [chr_name, chr_item] : reader.chr_map) {
            chr_map[py::str(chr_name)] = py::dict(
                py::arg("id")=chr_item.id,
                py::arg("index")=chr_item.index,
                py::arg("size")=chr_item.size
            );
        }
    }

    py::list py_get_overlapping_chunks(
        const str& chr_id,
        i64 start,
        i64 end
    ) {
        auto chunks = reader.get_overlapping_chunks(chr_id, start, end);
        py::list py_chunks;
        for (const auto& chunk : chunks) {
            py::dict py_chunk;
            py_chunk["file_start"] = chunk.start >> 16; // compressed file offset
            py_chunk["file_end"] = chunk.end >> 16; // compressed file offset
            py_chunk["block_start"] = chunk.start & 0xFFFF; // uncompressed block offset
            py_chunk["block_end"] = chunk.end & 0xFFFF; // uncompressed block offset
            py_chunks.append(py_chunk);
        }
        return py_chunks;
    }



};







class PyHiCReader {
    HiCReader reader;

public:
    py::dict header;
    py::dict footer;
    py::dict chr_sizes;
    py::list normalizations;
    py::list units;
    py::list bin_sizes;
    
    PyHiCReader(
        const str& path,
        i64 parallel = 24,
        i64 file_buffer_size = 32768,
        i64 max_file_buffer_count = 128
    ) : reader(path, parallel, file_buffer_size, max_file_buffer_count) {

        header["version"] = reader.header.version;
        header["footer_position"] = reader.header.footer_position;
        header["genome_id"] = reader.header.genome_id;
        header["nvi_position"] = reader.header.nvi_position;
        header["nvi_length"] = reader.header.nvi_length;
        header["attributes"] = py::dict();
        for (const auto& [key, value] : reader.header.attributes) {
            header["attributes"][py::str(key)] = value;
        }
        header["chr_map"] = py::dict();
        for (const auto& [chr_name, chr_item] : reader.header.chr_map) {
            header["chr_map"][py::str(chr_name)] = py::dict(
                py::arg("index")=chr_item.index,
                py::arg("size")=chr_item.size
            );
        }
        header["bp_resolutions"] = reader.header.bp_resolutions;
        header["frag_resolutions"] = reader.header.frag_resolutions;
        header["sites"] = reader.header.sites;

        footer["byte_count_v5"] = reader.footer.byte_count_v5;
        footer["attributes"] = py::dict();
        for (const auto& [key, value] : reader.footer.attributes) {
            footer["attributes"][py::str(key)] = value;
        }
        footer["master_index"] = py::dict();
        for (const auto& [key, item] : reader.footer.master_index) {
            footer["master_index"][py::str(key)] = py::dict(
                py::arg("position")=item.position,
                py::arg("size")=item.size
            );
        }
        py::list py_expected_value_vectors;
        for (const auto& [key, vector] : reader.footer.expected_value_vectors) {
            auto py_vector = py::dict();
            py_vector["normalization"] = vector.normalization;
            py_vector["unit"] = vector.unit;
            py_vector["bin_size"] = vector.bin_size;
            py_vector["value_count"] = vector.values.size();
            py_vector["chr_scale_factors"] = py::dict();
            for (const auto& [chr_index, scale_factor] : vector.chr_scale_factors) {
                py_vector["chr_scale_factors"][py::int_(chr_index)] = scale_factor;
            }
            py_expected_value_vectors.append(py_vector);
        }
        footer["expected_value_vectors"] = py_expected_value_vectors;
        py::list py_normalization_vectors;
        for (const auto& [key, vector] : reader.footer.normalization_vectors) {
            py_normalization_vectors.append(py::dict(
                py::arg("normalization")=vector.normalization,
                py::arg("chr_index")=vector.chr_index,
                py::arg("unit")=vector.unit,
                py::arg("bin_size")=vector.bin_size,
                py::arg("position")=vector.position,
                py::arg("byte_count")=vector.byte_count
            ));
        }
        footer["normalization_vectors"] = py_normalization_vectors;

        for (const auto& [key, chr] : reader.header.chr_map) {
            if (key == "All") continue;
            chr_sizes[py::str(key)] = chr.size;
        }
        for (const auto& norm : reader.footer.normalizations)
            normalizations.append(py::str(norm));
        for (const auto& unit : reader.footer.units)
            units.append(py::str(unit));
        for (const auto& bin_size : reader.header.bp_resolutions)
            bin_sizes.append(py::int_(bin_size));
    }

    py::array_t<f32> py_get_normalization_vector(
        const str& chr_id,
        const str& normalization,
        i64 bin_size,
        const str& unit
    ) {
        auto chr_index = reader.header.chr_map.at(chr_id).index;
        auto vector_ptr = reader.get_normalization_vector(
            chr_index, normalization, bin_size, unit
        );
        return py::array_t<f32>(
            vector_ptr->size(),
            vector_ptr->data(),
            py::cast(this) // Keep PyHiCReader alive
        );
    }

    py::dict py_get_matrix_metadata(
        const str& chr1_id,
        const str& chr2_id,
        i64 bin_size,
        const str& unit
    ) {
        auto chr1_index = reader.header.chr_map.at(chr1_id).index;
        auto chr2_index = reader.header.chr_map.at(chr2_id).index;
        auto matrix_metadata = reader.get_matrix_metadata(
            chr1_index, chr2_index, bin_size, unit
        );
        py::dict py_matrix_metadata;
        py_matrix_metadata["sum_counts"] = matrix_metadata->sum_counts;
        py_matrix_metadata["block_bin_count"] = matrix_metadata->block_bin_count;
        py_matrix_metadata["block_column_count"] = matrix_metadata->block_column_count;
        py::dict py_blocks;
        for (const auto& block : matrix_metadata->blocks) {
            py::dict py_block;
            py_block["position"] = block.second.position;
            py_block["size"] = block.second.size;
            py_blocks[py::int_(block.first)] = py_block;
        }
        py_matrix_metadata["blocks"] = py_blocks;
        return py_matrix_metadata;
    }

    py::dict py_parse_loc(
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
        auto loc = reader.parse_loc(
            chr_ids, starts, ends, centers, span,
            bin_size, bin_count, full_bin, unit);
        if (loc.reversed) std::swap(loc.x, loc.y);
        py::dict py_loc;
        py_loc["x"] = py::dict(
            py::arg("chr_id")=loc.x.chr.id,
            py::arg("chr_index")=loc.x.chr.index,
            py::arg("start")=loc.x.start,
            py::arg("end")=loc.x.end,
            py::arg("binned_start")=loc.x.binned_start,
            py::arg("binned_end")=loc.x.binned_end,
            py::arg("bin_start")=loc.x.bin_start,
            py::arg("bin_end")=loc.x.bin_end
        );
        py_loc["y"] = py::dict(
            py::arg("chr_id")=loc.y.chr.id,
            py::arg("chr_index")=loc.y.chr.index,
            py::arg("start")=loc.y.start,
            py::arg("end")=loc.y.end,
            py::arg("binned_start")=loc.y.binned_start,
            py::arg("binned_end")=loc.y.binned_end,
            py::arg("bin_start")=loc.y.bin_start,
            py::arg("bin_end")=loc.y.bin_end
        );
        py_loc["bin_size"] = loc.bin_size;
        return py_loc;
    }

    py::array_t<f32> py_read_signal(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        i64 bin_size = -1,
        i64 bin_count = -1,
        bool exact_bin_count = false,
        bool full_bin = false,
        f32 def_value = 0.0f,
        bool triangle = false,
        i64 min_distance_from_diagonal = -1,
        i64 max_distance_from_diagonal = -1,
        const str& normalization = "none",
        const str& mode = "observed",
        const str& unit = "bp",
        const str& save_to = ""
    ) {
        auto loc = reader.parse_loc(
            chr_ids, starts, ends, centers, span,
            bin_size, bin_count, full_bin, unit);
        std::vector<f32> signal;
        std::vector<size_t> shape;
        {
            py::gil_scoped_release release;
            signal = reader.read_signal(
                loc,
                def_value, triangle,
                min_distance_from_diagonal,
                max_distance_from_diagonal,
                normalization, mode, unit
            );
            if (exact_bin_count && bin_count >= 0) {
                std::vector<i64> old_shape = {
                    static_cast<i64>(loc.x.bin_end - loc.x.bin_start),
                    static_cast<i64>(loc.y.bin_end - loc.y.bin_start)
                };
                std::vector<i64> new_shape = {bin_count, bin_count};
                signal = resize_2d_array(signal, old_shape, new_shape);
                shape = {
                    static_cast<size_t>(bin_count),
                    static_cast<size_t>(bin_count)
                };
            } else {
                shape = {
                    static_cast<size_t>(loc.x.bin_end - loc.x.bin_start),
                    static_cast<size_t>(loc.y.bin_end - loc.y.bin_start)
                };
            }
            if (save_to != "") {
                save_npz(
                    save_to,
                    std::make_tuple("values", std::move(signal), shape)
                );
            }
        }
        if (save_to != "") return py::array_t<f32>(0);
        std::vector<size_t> strides = {shape[1] * sizeof(f32), sizeof(f32)};
        return py::array_t<f32>(shape, strides, signal.data());
    }

    py::dict py_read_sparse_signal(
        const std::vector<str>& chr_ids,
        const std::vector<i64>& starts = {},
        const std::vector<i64>& ends = {},
        const std::vector<i64>& centers = {},
        i64 span = -1,
        i64 bin_size = -1,
        i64 bin_count = -1,
        bool exact_bin_count = false,
        bool full_bin = false,
        bool triangle = false,
        i64 min_distance_from_diagonal = -1,
        i64 max_distance_from_diagonal = -1,
        const str& normalization = "none",
        const str& mode = "observed",
        const str& unit = "bp",
        const str& save_to = ""
    ) {
        auto loc = reader.parse_loc(
            chr_ids, starts, ends, centers, span,
            bin_size, bin_count, full_bin, unit);
        Sparse2DArray<f32> signal;
        {
            py::gil_scoped_release release;
            signal = reader.read_sparse_signal(
                loc,
                triangle,
                min_distance_from_diagonal,
                max_distance_from_diagonal,
                normalization, mode, unit
            );
            if (exact_bin_count && bin_count >= 0) {
                std::array<u32, 2> new_shape = {
                    static_cast<u32>(bin_count),
                    static_cast<u32>(bin_count)
                };
                signal = resize_2d_array(signal, new_shape);
            }
            if (save_to != "") {
                std::vector<u32> shape_vec(signal.shape.begin(), signal.shape.end());
                save_npz(
                    save_to,
                    std::make_tuple("values", std::move(signal.values), std::vector<size_t>{signal.values.size()}),
                    std::make_tuple("row", std::move(signal.row), std::vector<size_t>{signal.row.size()}),
                    std::make_tuple("col", std::move(signal.col), std::vector<size_t>{signal.col.size()}),
                    std::make_tuple("shape", std::move(shape_vec), std::vector<size_t>{2})
                );
            }
        }
        if (save_to != "") return py::dict();
        py::dict result;
        result["values"] = py::array_t<f32>(signal.values.size(), signal.values.data());
        result["row"] = py::array_t<u32>(signal.row.size(), signal.row.data());
        result["col"] = py::array_t<u32>(signal.col.size(), signal.col.data());
        result["shape"] = signal.shape;
        return result;
    }


};


py::object py_open(const str& path, const str& mode, py::kwargs kwargs) {
    OrderedMap<str, str> extensions = {
        {"bw", "bbi"}, {"bigwig", "bbi"}, {"bb", "bbi"}, {"bigbed", "bbi"},
        {"bam", "bam"},
        {"hic", "hic"}
    };
    std::vector<u32> bbi_magics = {
        BIGWIG_MAGIC, BIGBED_MAGIC, BIGWIG_MAGIC_SWAPPED, BIGBED_MAGIC_SWAPPED
    };
    str format = extensions.get(to_lowercase(split_string(path, '.').back()), "");
    if (format == "" && mode == "r") {
        auto buffer = open_file(path)->read(4, 0);
        if (buffer.size() == 4) {
            if (is_in(buffer.read<u32>(0), bbi_magics)) {
                format = "bbi";
            } else if (buffer.read_string(0, 4) == "BAM\1") {
                format = "bam";
            } else if (buffer.read_string(0, 4) == "HIC") {
                format = "hic";
            }
        }
    }
    if (format == "bbi") {
        if (mode == "r") {
            i64 parallel = kwargs.contains("parallel") ? kwargs["parallel"].cast<i64>() : 24;
            f64 zoom_correction = kwargs.contains("zoom_correction") ? kwargs["zoom_correction"].cast<f64>() : 1.0/3.0;
            i64 file_buffer_size = kwargs.contains("file_buffer_size") ? kwargs["file_buffer_size"].cast<i64>() : 32768;
            i64 max_file_buffer_count = kwargs.contains("max_file_buffer_count") ? kwargs["max_file_buffer_count"].cast<i64>() : 128;
            return py::cast(new PyBBIReader(path, parallel, zoom_correction, file_buffer_size, max_file_buffer_count), py::return_value_policy::take_ownership);
        } else if (mode == "w") {
            const str& type = kwargs.contains("type") ? kwargs["type"].cast<str>() : "bigwig";
            return py::cast(new PyBBIWriter(path, type), py::return_value_policy::take_ownership);
        }
    } else if (format == "bam") {
        if (mode == "r") {
            i64 parallel = kwargs.contains("parallel") ? kwargs["parallel"].cast<i64>() : 24;
            i64 file_buffer_size = kwargs.contains("file_buffer_size") ? kwargs["file_buffer_size"].cast<i64>() : 32768;
            i64 max_file_buffer_count = kwargs.contains("max_file_buffer_count") ? kwargs["max_file_buffer_count"].cast<i64>() : 128;
            str index_path = kwargs.contains("index_path") ? kwargs["index_path"].cast<str>() : "";
            return py::cast(new PyBAMReader(path, parallel, file_buffer_size, max_file_buffer_count, index_path), py::return_value_policy::take_ownership);
        } else if (mode == "w") {
            throw std::invalid_argument("BAM writing not implemented");
        }
    } else if (format == "hic") {
        if (mode == "r") {
            i64 parallel = kwargs.contains("parallel") ? kwargs["parallel"].cast<i64>() : 24;
            i64 file_buffer_size = kwargs.contains("file_buffer_size") ? kwargs["file_buffer_size"].cast<i64>() : 32768;
            i64 max_file_buffer_count = kwargs.contains("max_file_buffer_count") ? kwargs["max_file_buffer_count"].cast<i64>() : 128;
            return py::cast(new PyHiCReader(path, parallel, file_buffer_size, max_file_buffer_count), py::return_value_policy::take_ownership);
        } else if (mode == "w") {
            throw std::invalid_argument("HiC writing not implemented");
        }
    } else {
        throw std::invalid_argument("format of " + path + " not recognized");
    }
    throw std::invalid_argument("mode " + mode + " invalid");
}


std::vector<py::array_t<u32>> compress_sparse_by_color(
    const std::vector<f32> &values,
    const std::vector<u32> &row,
    const std::vector<u32> &col,
    u32 color_count
) {
    f32 min_value = 0.0f;
    f32 max_value = *std::max_element(values.begin(), values.end());
    std::vector<std::vector<u32>> result(color_count);
    for (u64 i = 0; i < values.size(); i++) {
        f32 value = (values[i] - min_value) / (max_value - min_value);
        if (std::isnan(value) || std::isinf(value)) continue;
        u32 value_bin = static_cast<u32>(std::floor(value * (color_count - 1)));
        u32 row_index = row[i];
        u32 col_index = col[i];
        auto &result_bin = result[value_bin];
        if (!result_bin.empty()) {
            if (result_bin[result_bin.size() - 3] == row_index
            && result_bin[result_bin.size() - 2] + result_bin[result_bin.size() - 1] == col_index) {
                result_bin[result_bin.size() - 1] = result_bin[result_bin.size() - 1] + 1;
                continue;
            }
        }
        result_bin.insert(result_bin.end(), {row_index, col_index, 1});
    }
    std::vector<py::array_t<u32>> py_result(color_count);
    for (u32 i = 0; i < color_count; i++) {
        std::vector<size_t> shape = {result[i].size() / 3, 3};
        std::vector<size_t> strides = {3 * sizeof(u32), sizeof(u32)};
        py_result[i] = py::array_t<u32>(shape, strides, result[i].data());
    }
    return py_result;
}


PYBIND11_MODULE(gwseq_io, m) {
    m.doc() = "Process BBI (bigWig/bigBed) and HiC files";

    m.attr("__version__") = "0.0.8";

    m.def("get_chr_sizes", &py_get_chr_sizes,
        "Get chromosome sizes for a given genome",
        py::arg("genome")
    );

    m.def("open", &py_open,
        "Open a bigWig, bigBed or HiC file",
        py::arg("path"),
        py::arg("mode") = "r"
    );

    py::class_<PyBBIReader>(m, "BBIReader", py::module_local())
        .def(py::init<const str&, i64, f64, i64, i64>(),
            "Reader for bigWig and bigBed files",
            py::arg("path"),
            py::arg("parallel") = 24,
            py::arg("zoom_correction") = 1.0/3.0,
            py::arg("file_buffer_size") = 32768,
            py::arg("max_file_buffer_count") = 128
        )
        .def_readonly("bbi_header", &PyBBIReader::bbi_header)
        .def_readonly("auto_sql", &PyBBIReader::auto_sql)
        .def_readonly("total_summary", &PyBBIReader::total_summary)
        .def_readonly("chr_tree_header", &PyBBIReader::chr_tree_header)
        .def_readonly("zoom_headers", &PyBBIReader::zoom_headers)
        .def_readonly("chr_sizes", &PyBBIReader::chr_sizes)
        .def_readonly("type", &PyBBIReader::type)
        .def_readonly("data_count", &PyBBIReader::data_count)
        .def("parse_locs", &PyBBIReader::py_parse_locs,
            "Parse locations and bins",
            py::arg("chr_ids"),
            py::arg("starts")  = std::vector<i64>{},
            py::arg("ends") = std::vector<i64>{},
            py::arg("centers") = std::vector<i64>{},
            py::arg("span") = -1,
            py::arg("bin_size") = 1,
            py::arg("bin_count") = -1,
            py::arg("full_bin") = false
        )
        .def("read_signal", &PyBBIReader::py_read_signal,
            "Read values from bigWig file",
            py::arg("chr_ids"),
            py::arg("starts")  = std::vector<i64>{},
            py::arg("ends") = std::vector<i64>{},
            py::arg("centers") = std::vector<i64>{},
            py::arg("span") = -1,
            py::arg("bin_size") = 1,
            py::arg("bin_count") = -1,
            py::arg("bin_mode") = "mean",
            py::arg("full_bin") = false,
            py::arg("def_value") = 0.0f,
            py::arg("zoom") = -1,
            py::arg("progress") = py::none()
        )
        .def("quantify", &PyBBIReader::py_quantify,
            "Quantify values from bigWig file",
            py::arg("chr_ids"),
            py::arg("starts")  = std::vector<i64>{},
            py::arg("ends") = std::vector<i64>{},
            py::arg("centers") = std::vector<i64>{},
            py::arg("span") = -1,
            py::arg("bin_size") = 1.0,
            py::arg("full_bin") = false,
            py::arg("def_value") = 0.0f,
            py::arg("reduce") = "mean",
            py::arg("zoom") = -1,
            py::arg("progress") = py::none()
        )
        .def("profile", &PyBBIReader::py_profile,
            "Profile values from bigWig file",
            py::arg("chr_ids"),
            py::arg("starts")  = std::vector<i64>{},
            py::arg("ends") = std::vector<i64>{},
            py::arg("centers") = std::vector<i64>{},
            py::arg("span") = -1,
            py::arg("bin_size") = 1,
            py::arg("bin_count") = -1,
            py::arg("bin_mode") = "mean",
            py::arg("full_bin") = false,
            py::arg("def_value") = 0.0f,
            py::arg("reduce") = "mean",
            py::arg("zoom") = -1,
            py::arg("progress") = py::none()
        )
        .def("read_entries", &PyBBIReader::py_read_entries,
            "Read entries from bigBed file",
            py::arg("chr_ids"),
            py::arg("starts")  = std::vector<i64>{},
            py::arg("ends") = std::vector<i64>{},
            py::arg("centers") = std::vector<i64>{},
            py::arg("span") = -1,
            py::arg("bin_size") = 1.0,
            py::arg("full_bin") = false,
            py::arg("progress") = py::none()
        )
        .def("to_bedgraph", &PyBBIReader::py_to_bedgraph,
            "Convert bigWig file to bedGraph format",
            py::arg("output_path"),
            py::arg("chr_ids") = std::vector<str>{},
            py::arg("bin_size") = 1.0,
            py::arg("zoom") = -1,
            py::arg("progress") = py::none()
        )
        .def("to_wig", &PyBBIReader::py_to_wig,
            "Convert bigWig file to WIG format",
            py::arg("output_path"),
            py::arg("chr_ids") = std::vector<str>{},
            py::arg("bin_size") = 1.0,
            py::arg("zoom") = -1,
            py::arg("progress") = py::none()
        )
        .def("to_bed", &PyBBIReader::py_to_bed,
            "Convert bigBed file to BED format",
            py::arg("output_path"),
            py::arg("chr_ids") = std::vector<str>{},
            py::arg("col_count") = 0,
            py::arg("progress") = py::none()
        );

    py::class_<PyBBIWriter>(m, "BBIWriter", py::module_local())
        .def(py::init<const str&, const str&>(),
            "Writer for bigWig and bigBed files",
            py::arg("path"),
            py::arg("type") = "bigwig"
        );

    py::class_<PyBAMReader>(m, "BAMReader", py::module_local())
        .def(py::init<const str&, i64, i64, i64, const str&>(),
            "Reader for BAM files",
            py::arg("path"),
            py::arg("parallel") = 24,
            py::arg("file_buffer_size") = 32768,
            py::arg("max_file_buffer_count") = 128,
            py::arg("index_path") = ""
        )
        .def_readonly("header", &PyBAMReader::header)
        .def_readonly("chr_map", &PyBAMReader::chr_map)
        .def("get_overlapping_chunks", &PyBAMReader::py_get_overlapping_chunks,
            "Get overlapping chunks for a location",
            py::arg("chr_id"),
            py::arg("start"),
            py::arg("end")
        );

    py::class_<PyHiCReader>(m, "HiCReader", py::module_local())
        .def(py::init<const str&, i64, i64, i64>(),
            "Reader for Hi-C .hic files",
            py::arg("path"),
            py::arg("parallel") = 24,
            py::arg("file_buffer_size") = 32768,
            py::arg("max_file_buffer_count") = 128
        )
        .def_readonly("header", &PyHiCReader::header)
        .def_readonly("footer", &PyHiCReader::footer)
        .def_readonly("chr_sizes", &PyHiCReader::chr_sizes)
        .def_readonly("normalizations", &PyHiCReader::normalizations)
        .def_readonly("units", &PyHiCReader::units)
        .def_readonly("bin_sizes", &PyHiCReader::bin_sizes)
        .def("get_normalization_vector", &PyHiCReader::py_get_normalization_vector,
            "Get normalization vector for a chromosome",
            py::arg("chr_id"),
            py::arg("normalization"),
            py::arg("bin_size"),
            py::arg("unit") = "bp"
        )
        .def("get_matrix_metadata", &PyHiCReader::py_get_matrix_metadata,
            "Get matrix metadata for a chromosome pair",
            py::arg("chr1_id"),
            py::arg("chr2_id"),
            py::arg("bin_size"),
            py::arg("unit") = "bp"
        )
        .def("parse_loc", &PyHiCReader::py_parse_loc,
            "Parse locations and bins",
            py::arg("chr_ids"),
            py::arg("starts")  = std::vector<i64>{},
            py::arg("ends") = std::vector<i64>{},
            py::arg("centers") = std::vector<i64>{},
            py::arg("span") = -1,
            py::arg("bin_size") = -1,
            py::arg("bin_count") = -1,
            py::arg("full_bin") = false,
            py::arg("unit") = "bp"
        )
        .def("read_signal", &PyHiCReader::py_read_signal,
            "Read values from Hi-C .hic file",
            py::arg("chr_ids"),
            py::arg("starts")  = std::vector<i64>{},
            py::arg("ends") = std::vector<i64>{},
            py::arg("centers") = std::vector<i64>{},
            py::arg("span") = -1,
            py::arg("bin_size") = -1,
            py::arg("bin_count") = -1,
            py::arg("exact_bin_count") = false,
            py::arg("full_bin") = false,
            py::arg("def_value") = 0.0f,
            py::arg("triangle") = false,
            py::arg("min_distance") = -1,
            py::arg("max_distance") = -1,
            py::arg("normalization") = "none",
            py::arg("mode") = "observed",
            py::arg("unit") = "bp",
            py::arg("save_to") = ""
        )
        .def("read_sparse_signal", &PyHiCReader::py_read_sparse_signal,
            "Read values from Hi-C .hic file",
            py::arg("chr_ids"),
            py::arg("starts")  = std::vector<i64>{},
            py::arg("ends") = std::vector<i64>{},
            py::arg("centers") = std::vector<i64>{},
            py::arg("span") = -1,
            py::arg("bin_size") = -1,
            py::arg("bin_count") = -1,
            py::arg("exact_bin_count") = false,
            py::arg("full_bin") = false,
            py::arg("triangle") = false,
            py::arg("min_distance") = -1,
            py::arg("max_distance") = -1,
            py::arg("normalization") = "none",
            py::arg("mode") = "observed",
            py::arg("unit") = "bp",
            py::arg("save_to") = ""
        );
    
    m.def("compress_sparse_by_color", &compress_sparse_by_color,
        "Compress sparse matrix by color",
        py::arg("values"),
        py::arg("row"),
        py::arg("col"),
        py::arg("color_count")
    );

}

