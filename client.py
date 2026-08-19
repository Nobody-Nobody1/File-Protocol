import os
import struct
import socket

def send_to_server(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 5000))  # connect to server
    sock.sendall(data)                 # send all frames
    sock.close()


def build_metadata_frame(filename):
    name_bytes = filename.encode("utf-8")
    name_len = len(name_bytes)
    filesize = os.path.getsize(filename)

    frame = bytearray()
    frame.append(0x01)  # FRAME_TYPE

    frame += struct.pack(">H", name_len)   # 2 bytes
    frame += name_bytes                    # N bytes
    frame += struct.pack(">Q", filesize)   # 8 bytes

    return frame

def build_chunk_frames(filename, chunk_size=4096):
    frames = []
    index = 0

    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            frame = bytearray()
            frame.append(0x02)  # FRAME_TYPE

            frame += struct.pack(">I", len(chunk))  # chunk size (4 bytes)
            frame += struct.pack(">I", index)       # chunk index (4 bytes)
            frame += chunk                          # raw data

            frames.append(frame)
            index += 1

    return frames

def build_end_frame():
    return bytearray([0x03])

if __name__ == "__main__":
    filename = "test.txt"

    # Build ONE continuous binary stream
    output = bytearray()

    # Add metadata frame
    output += build_metadata_frame(filename)

    # Add each chunk frame
    for frame in build_chunk_frames(filename):
        output += frame

    # Add end frame
    output += build_end_frame()

    send_to_server(output)