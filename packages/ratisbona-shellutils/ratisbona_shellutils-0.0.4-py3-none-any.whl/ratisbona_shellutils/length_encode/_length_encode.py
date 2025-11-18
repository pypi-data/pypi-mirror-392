def encode_rep_text(text: str) -> bytes:
    """
    Encodes a repetitive Text into a custom binary format.
    Useful if you want to compress ascii-art text.

    The format is as follows:
    - 4 bytes: Length of the character map
    - N bytes: Character map (UTF-8 encoded)
    - M bytes: Encoded data block. Each byte contains:
        - 4 bits: Character ID (index into character map) (1-15)
        - 4 bits: Repeat count (1-15)

    Args:
        text (str): The text to encode.

    Returns:
        bytes: The encoded data.

    Raises:
        ValueError: If the character map is full (more than 15 different characters in text)
    """
    encoded_data = bytearray()
    char_map = ""
    i = 0
    while i < len(text):
        char = text[i]
        if char not in char_map:
            if len(char_map) >= 15:
                raise ValueError("Character map is full!")
            char_map += char

        char_id = char_map.index(char)
        repeat_count = 1

        # Count how many times this character repeats (up to 15)
        while i + 1 < len(text) and text[i + 1] == char and repeat_count < 15:
            repeat_count += 1
            i += 1

        # Pack into a single byte: 4 bits for char ID, 4 bits for repeat count
        encoded_byte = (char_id << 4) | repeat_count
        encoded_data.append(encoded_byte)
        i += 1

    encoded_map = char_map.encode("utf8")
    while len(encoded_map) % 2 != 0:
        encoded_map += b"\0"
    length = len(encoded_map).to_bytes(4, byteorder="little")
    return length + encoded_map + bytes(encoded_data)


def decode_rep_text(bytecode: bytes) -> str:
    """
    Decodes a repetitive Text from a custom binary format.

    See encode_rep_text for the format.

    Args:
        bytecode (bytes): The encoded data.

    Returns:
        str: The decoded text.
    """
    length = int.from_bytes(bytecode[:4], byteorder="little")
    char_map_bytes = bytecode[4 : length + 4]
    char_map = char_map_bytes.decode("utf8")
    data_block = bytecode[length + 4 :]

    decoded_text = []
    for byte in data_block:
        char_id = (byte >> 4) & 0x0F  # Extract character ID
        repeat_count = byte & 0x0F  # Extract repeat count

        if char_id < len(char_map):
            decoded_text.append(char_map[char_id] * repeat_count)

    return "".join(decoded_text)