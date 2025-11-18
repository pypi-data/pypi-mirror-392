# Destination: test_sixel_minimal.py
# Quick test to see which sixel path is being used and debug output

from PIL import Image
from io import BytesIO
import sys

# Create minimal test image: 4x4 red square
img = Image.new('RGB', (4, 4), (255, 0, 0))

# Test 1: Can PIL save as SIXEL?
print("Testing PIL sixel support...")
try:
    sixel_buffer = BytesIO()
    img.save(sixel_buffer, format='SIXEL')
    data = sixel_buffer.getvalue()
    print(f"✓ PIL sixel works! Length: {len(data)} bytes")
    print(f"First 100 bytes: {data[:100]}")
    print(f"Last 50 bytes: {data[-50:]}")
except Exception as e:
    print(f"✗ PIL sixel failed: {e}")
    print("Will use basic implementation")

# Test 2: Check what catpic generates
print("\nTesting catpic sixel generation...")
sys.path.insert(0, 'src')
from catpic.protocols.sixel import SixelGenerator

gen = SixelGenerator()

# Convert image to PNG
png_buffer = BytesIO()
img.save(png_buffer, format='PNG')
png_data = png_buffer.getvalue()

# Generate sixel
sixel_output = gen.generate(png_data)

print(f"Catpic output length: {len(sixel_output)} bytes")
print(f"First 200 bytes: {sixel_output[:200]}")
print(f"\nHex dump of first 100 bytes:")
for i in range(0, min(100, len(sixel_output)), 16):
    hex_part = ' '.join(f'{b:02x}' for b in sixel_output[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in sixel_output[i:i+16])
    print(f"{i:04x}: {hex_part:<48} {ascii_part}")
