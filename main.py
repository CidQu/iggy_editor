import json
from models.readChars import parse_file 
from models.app import FontViewerApp, runApp
from helpers.byteToHex import convert_bytes_to_hex

file_path = "iggy/deneme.iggy" # Change this with your actual iggy file name

parsed_result = parse_file(file_path) 

with open("json/fonts.json", "w") as f:
        json.dump(convert_bytes_to_hex(parsed_result), f, indent=4)

runApp(file_path)