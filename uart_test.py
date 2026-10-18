import os
import time
import serial

PORT = "COM4"       
BAUD = 115200
TOTAL = 32 * 1024
CHUNK_SIZE = 512

payload = os.urandom(TOTAL)
received = bytearray()
start = time.perf_counter()

with serial.Serial(
    PORT,
    BAUD,
    timeout=1,
    write_timeout=2,
    xonxoff=False,
    rtscts=False,
    dsrdtr=False,
) as ser:

    time.sleep(0.2)
    ser.reset_input_buffer()

    for offset in range(0, TOTAL, CHUNK_SIZE):
        chunk = payload[offset:offset + CHUNK_SIZE]

        ser.write(chunk)
        ser.flush()

        echoed = bytearray()
        deadline = time.perf_counter() + 1

        while len(echoed) < len(chunk):
            if time.perf_counter() >= deadline:
                break

            echoed.extend(ser.read(len(chunk) - len(echoed)))

        received.extend(echoed)

        if bytes(echoed) != chunk:
            print(f"FAIL at offset {offset}")
            print(f"Sent:     {chunk.hex(' ')}")
            print(f"Received: {bytes(echoed).hex(' ')}")
            break

elapsed = time.perf_counter() - start

print(f"Sent:     {TOTAL} bytes")
print(f"Received: {len(received)} bytes")
print(f"Elapsed:  {elapsed:.2f} seconds")
print(f"Rate:     {len(received) / elapsed / 1024:.2f} KiB/s")
print("PASS" if received == payload else "FAIL")
