


def read_until(file, delimiter, include=False, partial=False, chunk_size=4096, max_chunk_size=1048576):
    result = bytearray()
    initial_offset = file.tell()
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            if partial:
                return result
            raise EOFError("delimiter not found (end of file reached)")
        index = chunk.find(delimiter)
        if index != -1:
            if include:
                index += 1
            result.extend(chunk[:index])
            break
        if len(result) + len(chunk) > max_chunk_size:
            raise ValueError("delimiter not found (maximum size exceeded)")
        result.extend(chunk)
    file.seek(initial_offset + len(result) + (0 if include else len(delimiter)))
    return result

