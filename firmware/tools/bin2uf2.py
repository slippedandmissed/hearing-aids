"""Minimal UF2 writer for the XIAO nRF52840 (family 0xADA52840). Usage: python3 bin2uf2.py app.bin app.uf2 [base_addr=0x27000]"""
import struct, sys
src, dst = sys.argv[1], sys.argv[2]
base = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x27000
data = open(src, "rb").read()
data += b"\x00" * (-len(data) % 256)
n = len(data) // 256
with open(dst, "wb") as f:
    for i in range(n):
        payload = data[i * 256:(i + 1) * 256].ljust(476, b"\x00")
        hdr = struct.pack("<IIIIIIII", 0x0A324655, 0x9E5D5157, 0x00002000, base + i * 256, 256, i, n, 0xADA52840)
        f.write(hdr + payload + struct.pack("<I", 0x0AB16F30))
print(f"wrote {dst}: {n} blocks, base {hex(base)}")
