def find_and_print_sequences(file_path):
    # This is the magic sequence that used in font start.
    sequence = bytes.fromhex('C0688F6DF77F000020658F6DF77F0000A0658F6DF77F0000F0698F6DF77F')
    skip_bytes = 50

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

            # We will remove null bytes from the names so it will be normal ascii values
            # instead of Unicode-16LE
            data = data.replace(b'\x00', b'')
            try:
                print(data.decode('ascii')) # Decode and print
            except UnicodeDecodeError as e:
                print(f"Failed {start}: {e}")
            start = end + len(null_sequence) # Go-on

# Example usage
file_path = 'deneme.iggy'
find_and_print_sequences(file_path)
