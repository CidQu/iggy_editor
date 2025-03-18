import json
from models.readChars import parse_file
from helpers.byteToHex import convert_bytes_to_hex

parsed_result = parse_file("iggy/deneme.iggy")

with open("json/fonts.json", "w") as f:
        json.dump(convert_bytes_to_hex(parsed_result), f, indent=4)