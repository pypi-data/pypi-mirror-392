#include "util/main.cpp"


struct SAMHeaderField {
    str tag;
    str value;
};


struct SAMHeaderLine {
    str type;
    std::vector<SAMHeaderField> fields;
    
    str get(const str& tag, const str& default_value = "") const {
        for (const auto& field : fields) {
            if (field.tag == tag) return field.value;
        }
        return default_value;
    }
    
    bool has(const str& tag) const {
        for (const auto& field : fields) {
            if (field.tag == tag) return true;
        }
        return false;
    }
};


class SAMHeader {
public:
    std::vector<SAMHeaderLine> lines;
    
    SAMHeader() = default;
    
    SAMHeader(const str& text) {
        std::istringstream stream(text);
        str line;
        while (std::getline(stream, line)) {
            if (line.empty() || line[0] != '@') continue;
            SAMHeaderLine header_line;
            
            // Parse header type (first 3 characters: @XX)
            if (line.size() < 3) continue;
            header_line.type = line.substr(1, 2);
            
            // Handle @CO (comment) lines specially - no fields, just text
            if (header_line.type == "CO") {
                if (line.size() > 4) {
                    header_line.fields.push_back(SAMHeaderField{"", line.substr(4)});
                }
                lines.push_back(std::move(header_line));
                continue;
            }
            
            // Parse TAG:VALUE fields (tab-delimited)
            std::istringstream field_stream(line.substr(3));
            str field;
            while (std::getline(field_stream, field, '\t')) {
                if (field.empty()) continue;
                
                // Find the first colon
                size_t colon_pos = field.find(':');
                if (colon_pos == str::npos || colon_pos < 2) continue;
                
                str tag = field.substr(0, colon_pos);
                str value = field.substr(colon_pos + 1);
                
                header_line.fields.push_back(SAMHeaderField{tag, value});
            }
            
            lines.push_back(std::move(header_line));
        }
    }
    
    std::vector<SAMHeaderLine> get_lines(const str& type) const {
        std::vector<SAMHeaderLine> result;
        for (const auto& line : lines) {
            if (line.type == type) result.push_back(line);
        }
        return result;
    }
    
    SAMHeaderLine get_line(const str& type) const {
        for (const auto& line : lines) {
            if (line.type == type) return line;
        }
        return SAMHeaderLine{type, {}};
    }
    
    bool has_line(const str& type) const {
        for (const auto& line : lines) {
            if (line.type == type) return true;
        }
        return false;
    }

    OrderedMap<str, ChrItem> get_chr_map() const {
        OrderedMap<str, ChrItem> chr_map;
        i64 index = 0;
        for (const auto& line : lines) {
            if (line.type != "SQ") continue;
            ChrItem chr;
            chr.id = line.get("SN");
            chr.size = std::stoll(line.get("LN", "0"));
            chr.index = index++;
            chr_map.insert(chr.id, chr);
        }
        return chr_map;
    }

};


std::tuple<SAMHeader, OrderedMap<str, ChrItem>> read_bam_header(File& file) {
    DecompressionStream stream(file.to_stream(0));
    
    // Read magic
    if (stream.read(4).to_string() != "BAM\1") {
        throw std::runtime_error("invalid bam magic string");
    }
    
    // Read header text
    u32 l_text = stream.read<u32>();
    SAMHeader header(stream.read(l_text).to_string());
    
    // Read reference sequences
    u32 n_ref = stream.read<u32>();
    OrderedMap<str, ChrItem> chr_map;
    for (u32 i = 0; i < n_ref; ++i) {
        ChrItem chr;
        u32 l_name = stream.read<u32>();
        chr.id = stream.read(l_name).to_string();
        chr.index = static_cast<i64>(i);
        chr.size = static_cast<i64>(stream.read<u32>());
        chr_map.insert(chr.id, chr);
    }
    
    return {header, chr_map};
}
