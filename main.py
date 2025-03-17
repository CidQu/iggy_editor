import json

def find_and_store_sequences(file_path):
    sequence = bytes.fromhex('C0688F6DF77F000020658F6DF77F0000A0658F6DF77F0000F0698F6DF77F')
    skip_bytes = 50
    character_endings = [
        bytes.fromhex('00000000000000000100010000000000'),
        bytes.fromhex('00000000000000000000010000000000'),
        bytes.fromhex('00000000000000000100000000000000'),
        bytes.fromhex('00000000000000000000000000000000')
    ]
    pattern_start = b'\x50\x00\x08\x6b'
    null_sequence = b'\x00\x00'

    fonts = []  # List to store parsed font data

    with open(file_path, 'rb') as f:
        content = f.read()
        start = 0

        while True:
            start = content.find(sequence, start)
            if start == -1:
                break

            start += len(sequence) + skip_bytes
            end = content.find(null_sequence, start)
            if end == -1:
                break

            font_name = content[start:end].replace(b'\x00', b'').decode('ascii', errors='ignore')
            font_offset = start

            first_char_position = content.find(pattern_start, end)
            if first_char_position == -1:
                print(f"Skipping font '{font_name}' due to missing first character pattern.")
                start = end + len(null_sequence)
                continue

            charlist = []
            char_position = 0

            while True:
                character = content[first_char_position + char_position : first_char_position + char_position + 16]
                character_ending = content[first_char_position + char_position + 16 : first_char_position + char_position + 16 + 16]

                if character.startswith(pattern_start):
                    char_bytes = int.from_bytes(character, "little")
                    char_type = int.from_bytes(character[:4], "little")
                    charlist.append({
                        "char_bytes": char_bytes,
                        "char_type": char_type,
                        "char_offset": char_position
                    })

                if character_ending not in character_endings:
                    break  # End of characters

                char_position += 32  # Move to the next character

            fonts.append({
                "font_name": font_name,
                "font_offset": font_offset,
                "chars": charlist
            })

            start = end + len(null_sequence)  # Move forward

    # Save to JSON file
    with open("json/fonts.json", "w") as f:
        json.dump(fonts, f, indent=4)

    print(f"Processed {len(fonts)} fonts. Data saved to fonts.json.")

# Example usage
file_path = "iggy/deneme.iggy"
find_and_store_sequences(file_path)