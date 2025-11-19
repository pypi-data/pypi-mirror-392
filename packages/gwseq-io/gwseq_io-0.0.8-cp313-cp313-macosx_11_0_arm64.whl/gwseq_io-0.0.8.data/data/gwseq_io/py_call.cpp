#pragma once

#include "includes.cpp"


#if defined(NO_ZLIB) || defined(NO_CURL)

#include <pybind11/pybind11.h>
#include <pybind11/embed.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#endif


#ifdef NO_ZLIB

inline std::vector<u8> py_zlib_decompress(const std::vector<u8>& data) {
    py::gil_scoped_acquire acquire;
    
    try {
        py::module_ zlib = py::module_::import("zlib");
        
        // Convert vector to bytes
        py::bytes data_bytes(reinterpret_cast<const char*>(data.data()), data.size());
        
        // Call zlib.decompress
        py::bytes decompressed = zlib.attr("decompress")(data_bytes);
        
        // Convert back to vector
        std::string result_str = decompressed.cast<std::string>();
        return std::vector<u8>(result_str.begin(), result_str.end());
    } catch (const py::error_already_set& e) {
        throw std::runtime_error(std::string("python zlib decompress error: ") + e.what());
    }
}

inline std::vector<u8> py_zlib_compress(const std::vector<u8>& data, str format = "gzip", i8 compression_level = 1) {
    int window_bits = format == "gzip" ? (15 + 16) : (format == "zlib" ? 15 : -15); // -15 = raw deflate
    
    py::gil_scoped_acquire acquire;
    
    try {
        py::module_ zlib = py::module_::import("zlib");
        
        // Convert vector to bytes
        py::bytes data_bytes(reinterpret_cast<const char*>(data.data()), data.size());
        
        // Call zlib.compress with appropriate wbits
        py::object compressobj = zlib.attr("compressobj")(compression_level, py::int_(8), window_bits);
        py::bytes compressed_part = compressobj.attr("compress")(data_bytes);
        py::bytes compressed_final = compressobj.attr("flush")();
        
        // Concatenate the two parts
        std::string part1 = compressed_part.cast<std::string>();
        std::string part2 = compressed_final.cast<std::string>();
        std::vector<u8> result(part1.begin(), part1.end());
        result.insert(result.end(), part2.begin(), part2.end());
        
        return result;
    } catch (const py::error_already_set& e) {
        throw std::runtime_error(std::string("python zlib compress error: ") + e.what());
    }
}

#endif


#ifdef NO_CURL

inline i64 py_get_url_size(const str& url) {
    py::gil_scoped_acquire acquire;
    
    try {
        py::module_ urllib_request = py::module_::import("urllib.request");
        
        // Open URL with HEAD request to get content length
        py::object Request = urllib_request.attr("Request");
        py::object request = Request(url);
        request.attr("get_method") = py::cpp_function([]() { return "HEAD"; });
        
        py::object response = urllib_request.attr("urlopen")(request);
        
        // Get Content-Length header
        py::object headers = response.attr("headers");
        py::str content_length = headers.attr("get")("Content-Length");
        
        if (content_length.is_none()) {
            throw std::runtime_error("Content-Length header not available");
        }
        
        return content_length.cast<i64>();
    } catch (const py::error_already_set& e) {
        throw std::runtime_error(std::string("python url size error: ") + e.what());
    }
}

inline std::vector<u8> py_read_url_all(const str& url) {
    py::gil_scoped_acquire acquire;
    
    try {
        py::module_ urllib_request = py::module_::import("urllib.request");
        
        // Open URL and read all content
        py::object response = urllib_request.attr("urlopen")(url);
        py::bytes content = response.attr("read")();
        
        // Convert to vector
        std::string result_str = content.cast<std::string>();
        return std::vector<u8>(result_str.begin(), result_str.end());
    } catch (const py::error_already_set& e) {
        throw std::runtime_error(std::string("python url read error: ") + e.what());
    }
}

inline std::vector<u8> py_read_url(const str& url, i64 size, i64 offset) {
    py::gil_scoped_acquire acquire;
    
    try {
        py::module_ urllib_request = py::module_::import("urllib.request");
        
        // Create request with Range header
        py::object Request = urllib_request.attr("Request");
        py::object request = Request(url);
        
        // Set Range header for partial content
        std::string range_header = "bytes=" + std::to_string(offset) + "-" + std::to_string(offset + size - 1);
        request.attr("add_header")("Range", range_header);
        
        // Open URL and read content
        py::object response = urllib_request.attr("urlopen")(request);
        py::bytes content = response.attr("read")();
        
        // Convert to vector
        std::string result_str = content.cast<std::string>();
        return std::vector<u8>(result_str.begin(), result_str.end());
    } catch (const py::error_already_set& e) {
        throw std::runtime_error(std::string("python url read error: ") + e.what());
    }
}

#endif
