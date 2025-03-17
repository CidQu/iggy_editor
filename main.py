import json

def find_and_store_sequences(file_path):
    # Magic for font start
    sequence = bytes.fromhex('C0688F6DF77F000020658F6DF77F0000A0658F6DF77F0000F0698F6DF77F')
    skip_bytes = 50
    character_endings = [
        # These indicates something but I'm still not sure what
        bytes.fromhex('00000000000000000000000000000000'), # 0
        bytes.fromhex('00000000000000000000010000000000'), # 1
        bytes.fromhex('00000000000000000100000000000000'), # 2
        bytes.fromhex('00000000000000000100010000000000')  # 3
    ]
    pattern_start = b'\x50\x00\x08\x6b'
    null_sequence = b'\x00\x00'

    fonts = []  # List to store parsed font data

    with open(file_path, 'rb') as f:
        content = f.read()
        start = 0

        while True:
            start = content.find(sequence, start) # Search fonts
            if start == -1:
                break

            start += len(sequence) + skip_bytes
            end = content.find(null_sequence, start) # Find where font name ends (two nulls after name)
            if end == -1:
                break

            # Because font name encoded with Unicode 16LE we need to replace
            # null bytes then decode as ascii
            font_name = content[start:end].replace(b'\x00', b'').decode('ascii', errors='ignore')
            font_offset = start # Set out starting position to first byte of font

            first_char_position = content.find(pattern_start, end)
            if first_char_position == -1:
                print(f"Skipping font '{font_name}' due to missing first character pattern.")
                start = end + len(null_sequence)
                continue

            charlist = []
            char_position = 0 # Keep track of char position

            while True:
                # Get first char, then loop
                character = content[first_char_position + char_position : first_char_position + char_position + 16]
                # Get first char, trail. This should be in list "character_endings"
                character_ending = content[first_char_position + char_position + 16 : first_char_position + char_position + 16 + 16]

                # Check if char fits our rules
                if character.startswith(pattern_start):
                    char_bytes = int.from_bytes(character, "little")
                    char_type = int.from_bytes(character[:4], "little")
                    try:
                        charlist.append({
                            "char_bytes": char_bytes,
                            "char_type": character_endings.index(character_ending), # Save which trailling bytes have
                            "char_offset": first_char_position + char_position # Save offset of the char
                            # We will use this offset later to find the vector of the char
                        })
                    except:
                        charlist.append({
                            "char_bytes": char_bytes,
                            "char_type": -1, # If there is no trailling then save it as -1
                            "char_offset": first_char_position + char_position # Save offset of the char
                            # We will use this offset later to find the vector of the char
                        })

                if character_ending not in character_endings:
                    break  # End of chars

                char_position += 32  # Move to the next char

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