def find_and_print_sequences(file_path):
    # This is the magic sequence that used in font start.
    sequence = bytes.fromhex('C0688F6DF77F000020658F6DF77F0000A0658F6DF77F0000F0698F6DF77F')
    skip_bytes = 50

    # We have four different character endings, if those are not exist that means our character list ended.
    # As of tody I have no idea why they're different. I believe there should be something different.
    character_ending_1 = bytes.fromhex('00000000000000000100010000000000')
    character_ending_2 = bytes.fromhex('00000000000000000000010000000000')
    character_ending_3 = bytes.fromhex('00000000000000000100000000000000')
    character_ending_4 = bytes.fromhex('00000000000000000000000000000000')

    pattern_start = b'\x50\x00\x08\x6b'

    # Check when font file name ends.
    null_sequence = b'\x00\x00'

    with open(file_path, 'rb') as f:
        content = f.read()
        start = 0

        while True:
            start = content.find(sequence, start)

            if start == -1: # If none left then break while loop
                break

            start += len(sequence) + skip_bytes # Skip 50 bytes when magic sequence found

            end = content.find(null_sequence, start)

            if end == -1:
                break

            # Get data between null sequence and magic sequence + 50 nulls.
            # This is our font name in Unicode-16LE
            data = content[start:end]

            # We will remove null bytes from the names so it will be
            # normal ascii values instead of Unicode-16LE
            data = data.replace(b'\x00', b'')

            first_char_position = content.find(pattern_start, end)

            if first_char_position == -1:
                raise UnicodeDecodeError

            char_position = 0
            character = content[first_char_position : first_char_position + 16] # Skip 20 bytes after
            character_ending = content[first_char_position + 16 : first_char_position + 16 + 16]
            try:
                print(data.decode('ascii')) # Decode the font name and print
                print(f"Font file offset: {start}") # Print offset of the font file start.
                
                charlist = []
                if character.startswith(pattern_start): # This is to make sure we're in the correct offset
                    charlist.append(character)
                else:
                    raise UnicodeDecodeError
                
                while True:
                    # Now we need to find other chars, that means we need to search for every 32 byte.
                    char_position += 32
                    character = content[first_char_position + char_position : first_char_position + char_position + 16] 

                    # Then get the ending of that char
                    character_ending = content[first_char_position + char_position + 16 : first_char_position + char_position + 16 + 16]

                    # If ending is not one of the approved endings, break loop
                    if character_ending not in [character_ending_1, character_ending_2, character_ending_3, character_ending_4]:
                        if character.startswith(pattern_start): # Make sure we're not skipping any chars
                            charlist.append(character)
                        break
                    if character.startswith(pattern_start):
                        charlist.append(character)
                    
                print(f"Character count: {len(charlist)}")
                print("\n")
            except UnicodeDecodeError as e:
                print(f"Failed {start}: {e}")

            start = end + len(null_sequence) # Go-on

# Example usage
file_path = 'deneme.iggy'
find_and_print_sequences(file_path)
