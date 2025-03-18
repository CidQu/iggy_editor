import struct

def read_uint32(data, offset):
    return struct.unpack("<I", data[offset:offset+4])[0]

def read_int64(data, offset):
    return struct.unpack("<q", data[offset:offset+8])[0]

def read_ushort(data, offset):
    return struct.unpack("<H", data[offset:offset+2])[0]

def read_float(data, offset):
    return struct.unpack("<f", data[offset:offset+4])[0]

def read_wstring(data, offset):
    """Reads a null-terminated wide string (UTF-16LE)."""
    string_bytes = bytearray()  # Use bytearray instead of list
    i = offset
    while True:
        char_bytes = data[i:i+2]
        if char_bytes == b'\x00\x00':
            break
        string_bytes.extend(char_bytes)
        i += 2
    return string_bytes.decode('utf-16le')


def read_font(data, offset):
    """Reads font data from the given offset."""

    font_data = {}

    font_data["_offset_start"] = offset  # Store for debugging and offset calculations

    num_characters_offset = offset + 0x20
    num_characters = read_ushort(data, num_characters_offset)
    font_data["numCharacters"] = num_characters
    
    key_code_table_offset_offset = offset + 0x20 + 2 + 0x16
    key_code_table_offset = read_uint32(data, key_code_table_offset_offset) + offset
    font_data["keyCodeTableOffset"] = key_code_table_offset


    char_width_table_offset_offset = key_code_table_offset_offset + 4 + 4
    char_width_table_offset = read_uint32(data, char_width_table_offset_offset) + offset
    font_data["charWidthTableOffset"] = char_width_table_offset
    
    font_name_offset_start = char_width_table_offset_offset + 4 + 0x11c
    position = font_name_offset_start
    
    
    font_name = read_wstring(data,position)
    font_data["fontName"] = font_name
    
    
    string_length_bytes = len(font_name.encode('utf-16le')) + 2  # +2 for null terminator
    
    next_struct_offset = position + string_length_bytes

    padding = (8 - (string_length_bytes % 8)) % 8
    next_struct_offset += padding



    font_data["charList"] = []
    for _ in range(num_characters):
        char_data = {}
        char_data["unko1"] = read_uint32(data, next_struct_offset)
        char_data["unko2"] = read_uint32(data, next_struct_offset + 4)
        char_data["hasPoints"] = read_ushort(data, next_struct_offset + 8)
        char_data["unko3"] = read_ushort(data, next_struct_offset + 10)
        char_data["unko4"] = read_uint32(data, next_struct_offset + 12)
        char_data["unko5"] = read_ushort(data, next_struct_offset + 16)
        char_data["unko6"] = read_ushort(data, next_struct_offset + 18)
        char_data["unko7"] = read_uint32(data, next_struct_offset + 20)
        position1 = next_struct_offset + 24
        char_offset = read_uint32(data, position1)
        char_offsets = position1 + char_offset
        char_data["charOffset"] = char_offset
        char_data["_calculated_char_offset"] = char_offsets # For verification
        char_data["unko8"] = read_uint32(data, next_struct_offset + 28)

        
        if char_data["hasPoints"] == 1:
            char_data["a1"] = read_float(data, char_offsets)
            char_data["a2"] = read_float(data, char_offsets + 4)
            char_data["a3"] = read_float(data, char_offsets + 8)
            char_data["a4"] = read_float(data, char_offsets + 12)
            char_data["numChunks"] = read_uint32(data, char_offsets + 16 + 8)

        font_data["charList"].append(char_data)
        next_struct_offset += 32  # Size of the charList struct


    return font_data


def parse_file(file_path):
    """Parses the entire file and returns a structured dictionary."""

    with open(file_path, "rb") as f:
        data = f.read()

    header_length = read_uint32(data, 0x2C)
    header = data[0x30:0x30 + header_length + 0xC0]
    
    
    parsed_data = {
        "headerLength": header_length,
        "header": header,
        "offsets": []
    }

    pos = 0x30 + header_length + 0xC0
    for i in range(6):
        offset_data = {}
        offset_temp = read_int64(data, pos)
        offset_data["offset_temp"] = offset_temp
        offset_data["_calculated_offset"] = offset_temp + pos  # Store the calculated offset

        font_info = read_font(data, offset_temp + pos)
        offset_data["font"] = font_info
        parsed_data["offsets"].append(offset_data)
        pos += 8
    return parsed_data

# --- Example Usage ---
if __name__ == "__main__":
    file_path = "iggy/deneme.iggy"  # Replace with the actual file path
    parsed_result = parse_file(file_path)

    # Print the parsed data (for demonstration/debugging)
    print(parsed_result)