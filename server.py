import socket
import struct

def parse_metadata(data, offset):
    frame_type = data[offset]
    offset += 1

    if frame_type != 0x01:
        raise Exception("Expected metadata frame")

    filename_len = struct.unpack(">H", data[offset:offset+2])[0]
    offset += 2

    filename = data[offset:offset+filename_len].decode("utf-8")
    offset += filename_len

    filesize = struct.unpack(">Q", data[offset:offset+8])[0]
    offset += 8

    return filename, filesize, offset

def parse_chunk(data, offset):
    frame_type = data[offset]
    offset += 1

    if frame_type != 0x02:
        raise Exception("Expected chunk frame")

    chunk_size = struct.unpack(">I", data[offset:offset+4])[0]
    offset += 4

    chunk_index = struct.unpack(">I", data[offset:offset+4])[0]
    offset += 4

    chunk_data = data[offset:offset+chunk_size]
    offset += chunk_size

    return chunk_index, chunk_data, offset

def parse_end_frame(data, offset):
    frame_type = data[offset]
    offset += 1

    if frame_type != 0x03:
        raise Exception("Expected end frame")

    return offset

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen(1)
    print("Server listening on port 5000")

    while True:
        conn, addr = server.accept()
        print("Client connected:", addr)
        handle_client(conn)

def handle_client(conn):
    data = bytearray()

    while True:
        chunk = conn.recv(4096)
        if not chunk:
            break
        data += chunk

    offset = 0

    # Parse metadata
    filename, filesize, offset = parse_metadata(data, offset)
    print("Filename:", filename)
    print("Filesize:", filesize)

    # Write file
    with open(filename + ".copy", "wb") as f:
        while offset < len(data):
            frame_type = data[offset]

            if frame_type == 0x02:
                chunk_index, chunk_data, offset = parse_chunk(data, offset)
                f.write(chunk_data)

            elif frame_type == 0x03:
                offset = parse_end_frame(data, offset)
                print("Upload complete")
                break

            else:
                raise Exception("Unknown frame type:", frame_type)

    conn.close()

if __name__ == "__main__":
    start_server()