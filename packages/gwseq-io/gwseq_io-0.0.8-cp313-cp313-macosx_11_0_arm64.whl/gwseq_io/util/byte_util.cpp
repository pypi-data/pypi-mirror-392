#include "includes.cpp"


class ByteArray {
public:
    std::vector<u8> data;

    ByteArray() {}
    ByteArray(const std::vector<u8>& data) : data(data) {}
    ByteArray(std::vector<u8>&& data) : data(std::move(data)) {}

    static ByteArray from_string(const str& input) {
        std::vector<u8> bytes(input.begin(), input.end());
        return ByteArray(std::move(bytes));
    }

    template<typename Container>
    static ByteArray from_iterable(const Container& input) {
        using T = typename Container::value_type;
        std::vector<u8> bytes(input.size() * sizeof(T));
        if constexpr (std::is_same_v<Container, std::vector<T>> || std::is_array_v<Container>) {
            std::memcpy(bytes.data(), input.data(), bytes.size());
        } else {
            auto it = input.begin();
            for (size_t i = 0; i < input.size(); ++i, ++it) {
                std::memcpy(&bytes[i * sizeof(T)], &(*it), sizeof(T));
            }
        }
        return ByteArray(std::move(bytes));
    }

    auto begin() { return data.begin(); }
    auto end() { return data.end(); }
    auto begin() const { return data.begin(); }
    auto end() const { return data.end(); }

    bool empty() const {  return data.empty(); }
    i64 size() const { return static_cast<i64>(data.size()); }

    u8 operator[](i64 index) const { return data[index]; }
    u8& operator[](i64 index) { return data[index]; }

    void resize(i64 new_size) {
        data.resize(new_size);
    }

    void reserve(i64 new_capacity) {
        data.reserve(new_capacity);
    }

    void shrink_to_fit() {
        data.shrink_to_fit();
    }

    template<typename T>
    T read(i64 offset) const {
        if constexpr (std::is_same_v<T, u8>) {
            return data[offset];
        } else if constexpr (std::is_same_v<T, i8>) {
            return static_cast<i8>(data[offset]);
        } else {
            return *reinterpret_cast<const T*>(&data[offset]);
        }
    }

    template<typename T>
    std::vector<T> read_array(i64 count, i64 offset = 0) const {
        std::vector<T> values;
        values.reserve(count);
        i64 type_size = sizeof(T);
        i64 end_offset = offset + count * type_size;
        for (i64 i = offset; i < end_offset; i += type_size) {
            values.push_back(*reinterpret_cast<const T*>(&data[i]));
        }
        return values;
    }

    str read_string(i64 offset, i64 length, bool trim_null = true) const {
        if (trim_null) {
            auto null_index = std::find(data.begin() + offset, data.begin() + offset + length, 0);
            return str(data.begin() + offset, null_index);
        }
        return str(data.begin() + offset, data.begin() + offset + length);
    }

    str to_string(bool trim_null = true) const {
        if (trim_null) {
            auto null_index = std::find(data.begin(), data.end(), 0);
            return str(data.begin(), null_index);
        }
        return str(data.begin(), data.end());
    }

    i64 find(u8 byte, i64 offset = 0) const {
        for (i64 i = offset; i < size(); ++i) {
            if (data[i] == byte) return i;
        }
        return -1;
    }

    i64 find(const ByteArray& bytes, i64 offset = 0) const {
        if (bytes.empty()) return -1;
        i64 search_end = size() - bytes.size() + 1;
        for (i64 i = offset; i < search_end; ++i) {
            bool match = true;
            for (i64 j = 0; j < bytes.size(); ++j) {
                if (data[i + j] != bytes[j]) {
                    match = false;
                    break;
                }
            }
            if (match) return i;
        }
        return -1;
    }

    void slice(i64 offset, i64 length) {
        if (offset > size()) offset = size();
        if (offset + length > size()) length = size() - offset;
        data = std::vector<u8>(data.begin() + offset, data.begin() + offset + length);
    }

    ByteArray sliced(i64 offset, i64 length) const {
        if (offset > size()) offset = size();
        if (offset + length > size()) length = size() - offset;
        std::vector<u8> slice_data(data.begin() + offset, data.begin() + offset + length);
        return ByteArray(std::move(slice_data));
    }
    
    template<typename T>
    void slice_at(const T& delimiter, i64 offset = 0, bool include = false, bool partial = false) {
        auto index = find(delimiter, offset);
        if (index == -1) {
            if (partial) {
                slice(offset, size() - offset);
            } else {
                throw std::runtime_error("delimiter not found");
            }
        } else if (include) {
            i64 delimiter_length;
            if constexpr (std::is_same_v<T, u8>) {
                delimiter_length = 1;
            } else {
                delimiter_length = delimiter.size();
            }
            slice(offset, index - offset + delimiter_length);
        } else {
            slice(offset, index - offset);
        }
    }

    template<typename T>
    ByteArray sliced_at(const T& delimiter, i64 offset = 0, bool include = false, bool partial = false) const {
        auto index = find(delimiter, offset);
        if (index == -1) {
            if (partial) return sliced(offset, size() - offset);
            throw std::runtime_error("delimiter not found");
        } else if (include) {
            i64 delimiter_length;
            if constexpr (std::is_same_v<T, u8>) {
                delimiter_length = 1;
            } else {
                delimiter_length = delimiter.size();
            }
            return sliced(offset, index - offset + delimiter_length);
        } else {
            return sliced(offset, index - offset);
        }
    }

    void append(const ByteArray& other, i64 offset = 0, i64 length = -1) {
        if (length < 0) length = other.size() - offset;
        data.insert(data.end(), other.data.begin() + offset, other.data.begin() + offset + length);
    }

    void append(u8 byte) {
        data.push_back(byte);
    }

    ByteArray appended(const ByteArray& other, i64 offset = 0, i64 length = -1) const {
        std::vector<u8> combined_data = data;
        if (length < 0) length = other.size() - offset;
        combined_data.insert(combined_data.end(), other.data.begin() + offset, other.data.begin() + offset + length);
        return ByteArray(std::move(combined_data));
    }

    ByteArray appended(u8 byte) const {
        std::vector<u8> combined_data = data;
        combined_data.push_back(byte);
        return ByteArray(std::move(combined_data));
    }

    std::vector<str> read_lines() const {
        std::vector<str> lines;
        i64 line_start = 0;
        for (i64 i = 0; i < size(); ++i) {
            if (data[i] == '\n') {
                i64 line_end = i;
                if (line_end > line_start && data[line_end - 1] == '\r') line_end -= 1;
                lines.emplace_back(data.begin() + line_start, data.begin() + line_end);
                line_start = i + 1;
            }
        }
        if (line_start < size()) {
            i64 line_end = size();
            if (line_end > line_start && data[line_end - 1] == '\r') line_end -= 1;
            lines.emplace_back(data.begin() + line_start, data.begin() + line_end);
        }
        return lines;
    }

    ByteArray decompressed(i64 buffer_size = 32768, i64 max_size = 1073741824) const {
#ifdef NO_ZLIB
        return ByteArray(py_zlib_decompress(data));
#else
        if (buffer_size < 1 || buffer_size > max_size) {
            throw std::runtime_error("buffer size " + std::to_string(buffer_size) + " invalid");
        }
        std::vector<u8> decompressed_data;
        std::vector<u8> buffer(buffer_size);
        z_stream stream{};
        stream.avail_in = static_cast<uInt>(data.size());
        stream.next_in = const_cast<Bytef*>(data.data());
        int init_result = inflateInit2(&stream, 15 + 32);
        if (init_result != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for decompression: " + 
                str(stream.msg ? stream.msg : "unknown error"));
        }
        while (true) {
            stream.avail_out = static_cast<uInt>(buffer_size);
            stream.next_out = buffer.data();
            int ret = inflate(&stream, Z_NO_FLUSH);
            if (ret != Z_OK && ret != Z_STREAM_END) {
                str error_msg = "zlib decompression of " +
                    std::to_string(data.size()) + " bytes failed: ";
                if (ret == Z_STREAM_ERROR) {
                    error_msg += "invalid compression level";
                } else if (ret == Z_DATA_ERROR) {
                    error_msg += "invalid or incomplete deflate data";
                } else if (ret == Z_MEM_ERROR) {
                    error_msg += "out of memory";
                } else if (ret == Z_BUF_ERROR) {
                    error_msg += "no progress possible or output buffer too small";
                } else {
                    error_msg += "error code " + std::to_string(ret);
                }
                if (stream.msg) error_msg += " (" + str(stream.msg) + ")";
                inflateEnd(&stream);
                throw std::runtime_error(error_msg);
            }
            i64 decompressed = buffer_size - stream.avail_out;
            if (decompressed_data.size() + decompressed > static_cast<u64>(max_size)) {
                inflateEnd(&stream);
                throw std::runtime_error("decompressed data exceeds limit (" + std::to_string(max_size) + ")");
            }
            if (ret == Z_STREAM_END && decompressed_data.size() == 0 && decompressed == buffer_size) {
                decompressed_data = std::move(buffer);
                break;
            }
            decompressed_data.insert(decompressed_data.end(), buffer.begin(), buffer.begin() + decompressed);
            if (ret == Z_STREAM_END) break;
        }
        inflateEnd(&stream);
        return ByteArray(std::move(decompressed_data));
#endif
    }

#ifdef NO_ZLIB
    ByteArray compressed(str format = "gzip", i8 compression_level = 1) const {
        return ByteArray(py_zlib_compress(data, format, compression_level));
#else
    ByteArray compressed(str format = "gzip", i8 compression_level = Z_DEFAULT_COMPRESSION) const {
        uLong compressed_size = compressBound(static_cast<uLong>(data.size()));
        std::vector<u8> compressed_data(compressed_size);
        z_stream stream{};
        stream.avail_in = static_cast<uInt>(data.size());
        stream.next_in = const_cast<Bytef*>(data.data());
        stream.avail_out = static_cast<uInt>(compressed_size);
        stream.next_out = compressed_data.data();
        int window_bits = format == "gzip" ? (15 + 16) : (format == "zlib" ? 15 : -15); // -15 = raw deflate
        int init_result = deflateInit2(&stream, compression_level, Z_DEFLATED, window_bits, 8, Z_DEFAULT_STRATEGY);
        if (init_result != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for compression: " + 
                str(stream.msg ? stream.msg : "unknown error"));
        }
        int ret = deflate(&stream, Z_FINISH);
        if (ret != Z_STREAM_END) {
            str error_msg = "zlib compression of " +
                std::to_string(data.size()) + " bytes failed: ";
            if (ret == Z_OK) {
                error_msg += "incomplete compression";
            } else if (ret == Z_STREAM_ERROR) {
                error_msg += "invalid compression level or parameters";
            } else if (ret == Z_BUF_ERROR) {
                error_msg += "no progress possible or output buffer too small";
            } else {
                error_msg += "error code " + std::to_string(ret);
            }
            if (stream.msg) error_msg += " (" + str(stream.msg) + ")";
            deflateEnd(&stream);
            throw std::runtime_error(error_msg);
        }
        compressed_data.resize(stream.total_out);
        deflateEnd(&stream);
        return ByteArray(std::move(compressed_data));
#endif
    }

};


class ByteStream {
    std::function<ByteArray()> input_function;
    ByteArray chunk;
    i64 chunk_offset = 0;

public:
    ByteStream() = default;
    
    ByteStream(
        std::function<ByteArray()> input_function
    ) : input_function(input_function) {}
    
    ByteStream(
        std::shared_ptr<ByteStream> input_stream
    ) {
        throw std::runtime_error("not implemented (useless, use input_stream directly)");
    }

    virtual ~ByteStream() = default;

    // Delete copy constructor and copy assignment (move-only semantics)
    ByteStream(const ByteStream&) = delete;
    ByteStream& operator=(const ByteStream&) = delete;
    
    // Default move constructor and move assignment
    ByteStream(ByteStream&&) = default;
    ByteStream& operator=(ByteStream&&) = default;

    template<typename T>
    struct InputState {
        T input;
        i64 offset = 0;
        i64 chunk_size;
    };

    static ByteStream from_bytes(
        ByteArray&& input,
        i64 chunk_size = 8192
    ) {
        auto state = std::make_shared<InputState<ByteArray>>(InputState<ByteArray>{
            std::move(input),
            0,
            chunk_size
        });
        return ByteStream(
            [state]() mutable -> ByteArray {
                if (state->offset >= state->input.size()) return ByteArray();
                i64 length = std::min(state->chunk_size, state->input.size() - state->offset);
                auto result = state->input.sliced(state->offset, length);
                state->offset += length;
                return result;
            }
        );
    }

    template<typename Container>
    static ByteStream from_iterable(
        Container&& input,
        i64 chunk_size = 8192
    ) {
        using T = typename std::decay_t<Container>::value_type;
        auto state = std::make_shared<InputState<std::decay_t<Container>>>(InputState<std::decay_t<Container>>{
            std::move(input),
            0,
            static_cast<i64>(((chunk_size + sizeof(T) - 1) / sizeof(T)) * sizeof(T))
        });
        return ByteStream(
            [state]() mutable -> ByteArray {
                i64 item_count = state->chunk_size / sizeof(T);
                i64 item_offset = state->offset / sizeof(T);
                if (item_offset >= static_cast<i64>(state->input.size())) return ByteArray();
                i64 length = std::min(item_count, static_cast<i64>(state->input.size()) - item_offset);
                auto start = state->input.begin() + item_offset;
                auto end = start + length;
                auto result = ByteArray::from_iterable(std::vector<T>(start, end));
                state->offset += length * sizeof(T);
                return result;
            }
        );
    }

    static ByteStream merge(
        std::vector<ByteStream>&& streams
    ) {
        struct MergeState {
            std::vector<ByteStream> streams;
            size_t current_index = 0;
        };
        auto state = std::make_shared<MergeState>();
        state->streams = std::move(streams);
        return ByteStream(
            [state]() mutable -> ByteArray {
                while (state->current_index < state->streams.size()) {
                    auto chunk = state->streams[state->current_index].read_chunk();
                    if (chunk.empty()) {
                        state->current_index++;
                        continue;
                    }
                    return chunk;
                }
                return ByteArray();
            }
        );
    }

    virtual ByteArray read_chunk() {
        if (chunk_offset < chunk.size()) {
            if (chunk_offset == 0) {
                chunk_offset = chunk.size();
                return std::move(chunk);
            }
            ByteArray result = chunk.sliced(chunk_offset, chunk.size() - chunk_offset);
            chunk_offset = chunk.size();
            return result;
        }
        chunk = input_function();
        chunk_offset = chunk.size();
        return std::move(chunk);
    }

    ByteArray read(i64 length, bool partial = false) {
        i64 available = chunk.size() - chunk_offset;
        if (length == available) {
            return read_chunk();
        } else if (length < available) {
            ByteArray result = chunk.sliced(chunk_offset, length);
            chunk_offset += length;
            return result;
        } else {
            ByteArray result;
            result.reserve(length);
            while (length > 0) {
                if (chunk_offset < chunk.size()) {
                    i64 cut = std::min(length, chunk.size() - chunk_offset);
                    result.append(chunk, chunk_offset, cut);
                    chunk_offset += cut;
                    length -= cut;
                } else {
                    chunk = read_chunk();
                    if (chunk.size() == 0) {
                        if (!partial) {
                            str message = "end of stream reached (" +
                                std::to_string(length) + " bytes missing)";
                            throw std::runtime_error(message);
                        }
                        return result;
                    }
                    chunk_offset = 0;
                }
            }
            return result;
        }
    }

    ByteArray read_until(
        u8 delimiter,
        bool include = false,
        bool partial = false,
        i64 max_size = 1048576
    ) {
        ByteArray result;
        while (result.size() < max_size) {
            if (chunk_offset < chunk.size()) {
                i64 index = chunk.find(delimiter, chunk_offset);
                if (index != -1) {
                    i64 cut = include ? index - chunk_offset + 1 : index - chunk_offset;
                    result.append(chunk, chunk_offset, cut);
                    chunk_offset = index + 1;
                    return result;
                }
                result.append(chunk, chunk_offset, chunk.size() - chunk_offset);
                chunk_offset = chunk.size();
            } else {
                chunk = read_chunk();
                if (chunk.size() == 0) {
                    if (!partial) throw std::runtime_error("delimiter not found (end of stream reached)");
                    return result;
                }
                chunk_offset = 0;
            }
        }
        throw std::runtime_error("delimiter not found (maximum size exceeded)");
    }

    void skip(i64 length, bool partial = false) {
        while (length > 0) {
            if (chunk_offset < chunk.size()) {
                i64 cut = std::min(length, chunk.size() - chunk_offset);
                chunk_offset += cut;
                length -= cut;
            } else {
                chunk = read_chunk();
                if (chunk.size() == 0) {
                    if (!partial) {
                        str message = "end of stream reached (" +
                            std::to_string(length) + " bytes missing)";
                        throw std::runtime_error(message);
                    }
                    return;
                }
                chunk_offset -= chunk.size();
            }
        }
    }

    template<typename T>
    T read() {
        return read(sizeof(T)).read<T>(0);
    }

    template<typename T>
    std::vector<T> read_array(i64 count) {
        return read(sizeof(T) * count).read_array<T>(count);
    }

    str read_string(i64 length, bool trim_null = true) {
        return read(length).to_string(trim_null);
    }

};


#ifdef NO_ZLIB

class CompressionStream : public ByteStream {
public:
    u32 crc32;
    i64 uncompressed_size;
    i64 compressed_size;

    CompressionStream(
        ByteStream input_stream,
        str format = "gzip",
        i8 compression_level = 1,
        i64 chunk_size = 8192,
        i64 buffer_size = 32768,
        bool compute_crc32 = false
    ) {
        throw std::runtime_error("zlib support not available");
    }

    ByteArray read_chunk() override {
        throw std::runtime_error("zlib support not available");
    }
};

class DecompressionStream : public ByteStream {
public:
    DecompressionStream(
        ByteStream input_stream,
        i64 chunk_size = 8192,
        i64 buffer_size = 32768
    ) {
        throw std::runtime_error("zlib support not available");
    }
    ByteArray read_chunk() override {
        throw std::runtime_error("zlib support not available");
    }
};

#else

class CompressionStream : public ByteStream {
    ByteStream input_stream;
    z_stream stream;
    bool initialized = false;
    bool finished = false;
    i64 chunk_size;
    i64 buffer_size;
    bool compute_crc32;
    ByteArray current_input_chunk; // Keep input buffer alive

public:
    u32 crc32;
    i64 uncompressed_size;
    i64 compressed_size;

    CompressionStream(
        ByteStream input_stream,
        str format = "gzip",
        i8 compression_level = Z_DEFAULT_COMPRESSION,
        i64 chunk_size = 8192,
        i64 buffer_size = 32768,
        bool compute_crc32 = false
    ) : input_stream(std::move(input_stream)), chunk_size(chunk_size), buffer_size(buffer_size),
        compute_crc32(compute_crc32), crc32(0), uncompressed_size(0), compressed_size(0) {
        stream = z_stream{};
        int window_bits = format == "gzip" ? (15 + 16) : (format == "zlib" ? 15 : -15);
        int ret = deflateInit2(&stream, compression_level, Z_DEFLATED, window_bits, 8, Z_DEFAULT_STRATEGY);
        if (ret != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for compression: " + 
                str(stream.msg ? stream.msg : "unknown error"));
        }
        initialized = true;
    }

    ~CompressionStream() {
        if (initialized) deflateEnd(&stream);
    }

    ByteArray read_chunk() override {
        if (finished) return ByteArray();
        std::vector<u8> output_buffer(buffer_size);
        stream.avail_out = static_cast<uInt>(buffer_size);
        stream.next_out = output_buffer.data();
        bool input_exhausted = false;
        while (stream.avail_out > 0) {
            if (stream.avail_in == 0 && !input_exhausted) {
                current_input_chunk = input_stream.read_chunk();
                if (current_input_chunk.empty()) {
                    input_exhausted = true;
                } else {
                    if (compute_crc32) {
                        crc32 = ::crc32(crc32, current_input_chunk.data.data(), static_cast<uInt>(current_input_chunk.size()));
                    }
                    uncompressed_size += current_input_chunk.size();
                    stream.avail_in = static_cast<uInt>(current_input_chunk.size());
                    stream.next_in = const_cast<Bytef*>(current_input_chunk.data.data());
                }
            }
            int flush_mode = input_exhausted ? Z_FINISH : Z_NO_FLUSH;
            int ret = deflate(&stream, flush_mode);
            if (ret == Z_STREAM_END) {
                finished = true;
                break;
            } else if (ret != Z_OK) {
                str error_msg = "zlib compression error: ";
                if (ret == Z_STREAM_ERROR) {
                    error_msg += "invalid compression level or parameters";
                } else if (ret == Z_BUF_ERROR) {
                    error_msg += "no progress possible or output buffer too small";
                } else {
                    error_msg += "error code " + std::to_string(ret);
                }
                if (stream.msg) error_msg += " (" + str(stream.msg) + ")";
                throw std::runtime_error(error_msg);
            }
            i64 bytes_written = buffer_size - stream.avail_out;
            if (bytes_written >= chunk_size || stream.avail_out == 0 || input_exhausted) {
                break;
            }
        }
        i64 bytes_written = buffer_size - stream.avail_out;
        if (bytes_written == 0) return ByteArray();
        compressed_size += bytes_written;
        output_buffer.resize(bytes_written);
        return ByteArray(std::move(output_buffer));
    }
};


class DecompressionStream : public ByteStream {
    ByteStream input_stream;
    z_stream stream;
    bool initialized = false;
    bool finished = false;
    i64 chunk_size;
    i64 buffer_size;
    ByteArray current_input_chunk; // Keep input buffer alive

public:
    DecompressionStream(
        ByteStream input_stream,
        i64 chunk_size = 8192,
        i64 buffer_size = 32768
    ) : input_stream(std::move(input_stream)), chunk_size(chunk_size), buffer_size(buffer_size) {
        stream = z_stream{};
        int ret = inflateInit2(&stream, 15 + 32); // Auto-detect gzip/zlib format
        if (ret != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for decompression: " + 
                str(stream.msg ? stream.msg : "unknown error"));
        }
        initialized = true;
    }

    ~DecompressionStream() {
        if (initialized) inflateEnd(&stream);
    }

    ByteArray read_chunk() override {
        if (finished) return ByteArray();
        std::vector<u8> output_buffer(buffer_size);
        stream.avail_out = static_cast<uInt>(buffer_size);
        stream.next_out = output_buffer.data();
        bool input_exhausted = false;
        while (stream.avail_out > 0) {
            if (stream.avail_in == 0 && !input_exhausted) {
                current_input_chunk = input_stream.read_chunk();
                if (current_input_chunk.empty()) {
                    input_exhausted = true;
                } else {
                    stream.avail_in = static_cast<uInt>(current_input_chunk.size());
                    stream.next_in = const_cast<Bytef*>(current_input_chunk.data.data());
                }
            }
            if (input_exhausted && stream.avail_in == 0) {
                break;
            }
            int ret = inflate(&stream, Z_NO_FLUSH);
            if (ret == Z_STREAM_END) {
                finished = true;
                break;
            } else if (ret != Z_OK) {
                str error_msg = "zlib decompression error: ";
                if (ret == Z_STREAM_ERROR) {
                    error_msg += "invalid compression level";
                } else if (ret == Z_DATA_ERROR) {
                    error_msg += "invalid or incomplete deflate data";
                } else if (ret == Z_MEM_ERROR) {
                    error_msg += "out of memory";
                } else if (ret == Z_BUF_ERROR) {
                    error_msg += "no progress possible";
                } else {
                    error_msg += "error code " + std::to_string(ret);
                }
                if (stream.msg) error_msg += " (" + str(stream.msg) + ")";
                throw std::runtime_error(error_msg);
            }
            i64 bytes_written = buffer_size - stream.avail_out;
            if (bytes_written >= chunk_size || stream.avail_out == 0 || input_exhausted) {
                break;
            }
        }
        i64 bytes_written = buffer_size - stream.avail_out;
        if (bytes_written == 0) return ByteArray();
        output_buffer.resize(bytes_written);
        return ByteArray(std::move(output_buffer));
    }
};

#endif
