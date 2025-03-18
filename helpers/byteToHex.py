def convert_bytes_to_hex(data):
    """Recursively converts bytes objects in a dictionary to hex strings."""
    if isinstance(data, dict):
        return {k: convert_bytes_to_hex(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_bytes_to_hex(item) for item in data]
    elif isinstance(data, bytes):
        return data.hex()
    else:
        return data