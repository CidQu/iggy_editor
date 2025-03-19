# IGGY File Format Notes

## Header

*   **Signature:** "x49 x67 x0A xED" (4 bytes, magic number: `Ig\n.` in ASCII)
*   **Version:** (unknown)
*   **SWF:** Written in Unicode-16LE (location unknown)
*   **File Start:** (unknown)
*   **First Font Offset:** `0x30 + header_length + 0xC0`
*   **Header Size:** 824 bytes.

## Font Hierarchy

This section describes the overall structure of the font data *within* an IGGY file.

*   **Font Header:**  Contains general information about a single font.
    *   Number of characters
    *   Offsets to keyCodeTable and charWidthTable
*   **Character List:** An array of structures, one for each character in the font.
    *   **Characters:** Offsets of vector table (if has any)
* **Texture List, Textures, Coordinates**
*   **keyCodeTable:**  Map of character codes written in Unicode 16LE, so it is possible to add Turkish characters
*   **charWidthTable:**  Don't know the details yet.
*   **4 nulls (separation between two fonts):**  Multiple font files are seperated with 4 nulls, if there are no nulls that means no bytes left to read.

## Font Data Block Structure

This section describes the detailed layout of a *single* font's data block.

*   **Magic Number:** `16 FF` (2 bytes)
*   **Skip 32 bytes**
*   **Number of Characters** (2 bytes, `ushort`)
*   **Skip 22 bytes**
*   **`keyCodeTable` Offset** (4 bytes, `int32`)
*   **Skip 4 bytes** (nulls)
*   **`charWidthTable` Offset** (4 bytes, `int32`)
*   **Skip 284 bytes** (0x11C)
*   **Font Name**  UTF-16LE string ends with nulls (x00x00)
* **Padding** After font name, align to 8-byte boundary. Calculation: `(8 - (string_length_bytes % 8)) % 8`.
*   **Character List** Starts after font name and padding.

## Character List Entry (32 bytes each)

This describes the structure of *each* entry in the `charList` array.

*   **`unko1`:** (4 bytes, `int32`) - Unknown (generally null).
*   **`unko2`:** (4 bytes, `int32`) - Unknown (generally null).
*   **`hasPoints`:** (2 bytes, `short`) - Flag indicating whether the character has vector data (1) or not (0).
*   **`unko3`:** (2 bytes, `short`) - Unknown (another flag? Probably).
*  **Magic Number:** `50 00 68 2C 5A 01` (6 bytes)
*   **`charOffset`:** (4 bytes, `int32`)
* **`unko8`**: (4 bytes, `int32`) - Unknown.

## Character Vector Data (Variable Size)

This section describes the data found at the offset specified by `charOffset`.  This data only exists if `hasPoints` is 1.

*   **`a1`:** (4 bytes, `float`) - Bounding box coordinate (likely x_min, y_min, x_max, or y_max. But for now I don't know for sure which is which).
*   **`a2`:** (4 bytes, `float`) - Bounding box coordinate.
*   **`a3`:** (4 bytes, `float`) - Bounding box coordinate.
*   **`a4`:** (4 bytes, `float`) - Bounding box coordinate.
*   **Magic number:** `x30` followed by 7 nulls (8 bytes).
*   **`numChunks`:** (4 bytes, `int32`) - Number of chunks
*   **Skip 36 bytes:** IDK What is written there (yet).
*   **Coordinates:** (24 bytes per coordinate set) - Explanied below

## Coordinates (24 bytes each)

*   **X:** (4 bytes)
*   **Y:** (4 bytes)
*   **Curve X:** (4 bytes) - If non-zero, indicates a curved segment.
*   **Curve Y:** (4 bytes) - If non-zero, indicates a curved segment.
*   **Line Type:** (4 bytes)
    *   `01`: Skip this point.
    *   `02`: Draw a straight line to this point.
    *   `03`: Draw a curved line to this point (using Curve X and Curve Y).
*    **Null:** (4 bytes)

### How many coordinates for one char?
`(char[i+1].vectorOffset - char[i].vectorOffset - 58) / 24`

Difference between next char’s and current char’s vector offsets, then minus 58 because we have 58 bytes of header in vector. Then divide that by 24 which in number of bytes each coordinate have. This equals to number of coordinate we have for one char.