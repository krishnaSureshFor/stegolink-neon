from PIL import Image

def hide_text(image_path, message, output_path):
    img = Image.open(image_path).convert("RGB")
    encoded = img.copy()
    w, h = img.size

    bits = ''.join(format(ord(c), '08b') for c in message)
    bits += "1111111111111110"  # EOF marker

    idx = 0
    for y in range(h):
        for x in range(w):
            if idx >= len(bits):
                break
            r, g, b = img.getpixel((x, y))
            new_r = (r & ~1) | int(bits[idx])
            encoded.putpixel((x, y), (new_r, g, b))
            idx += 1
        if idx >= len(bits):
            break

    encoded.save(output_path, "PNG")


def reveal_text(image_path):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    bits = ""

    for y in range(h):
        for x in range(w):
            r, g, b = img.getpixel((x, y))
            bits += str(r & 1)

    eof = "1111111111111110"
    pos = bits.find(eof)
    if pos != -1:
        bits = bits[:pos]

    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        chars.append(chr(int(byte, 2)))

    return ''.join(chars)
