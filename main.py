import json
from models.readChars import parse_file 
from models.app import FontViewerApp, runApp
from helpers.byteToHex import convert_bytes_to_hex
import sys

if len(sys.argv) > 1:
    mode = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else "iggy/deneme.iggy"
    if mode == "view":
        runApp(file_path)
        sys.exit(0)
    elif mode == "dump":
        parsed_result = parse_file(file_path) 
        with open("json/fonts.json", "w") as f:
            json.dump(convert_bytes_to_hex(parsed_result), f, indent=4)
        print("Dump successful")
        sys.exit(0)
else:
    print("Usage: python main.py [dump|view] <file_path>")
    sys.exit(1)