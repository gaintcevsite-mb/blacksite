import PIL.Image as Image

def make_transparent(input_path, output_path, tolerance=25):
    try:
        img = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {input_path}: {e}")
        return
        
    pixels = img.load()
    width, height = img.size
    
    soft_buffer = 40
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if r > 255 - tolerance and g > 255 - tolerance and b > 255 - tolerance:
                pixels[x, y] = (r, g, b, 0)
            else:
                if r > 255 - tolerance - soft_buffer and g > 255 - tolerance - soft_buffer and b > 255 - tolerance - soft_buffer:
                    brightness = (r + g + b) / 3.0
                    alpha = int(255 - ((brightness - (255 - tolerance - soft_buffer)) / soft_buffer) * 255)
                    alpha = max(0, min(255, alpha))
                    pixels[x, y] = (r, g, b, alpha)

    img.save(output_path)
    print(f"Saved {output_path}")

images = {
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/acq_bank_1775081778297.png": "img/acq_bank.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/acq_routing_1775081791190.png": "img/acq_routing.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/acq_chargeback_1775081803116.png": "img/acq_chargeback.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/acq_fraud_1775081818931.png": "img/acq_fraud.png"
}

for inp, out in images.items():
    make_transparent(inp, out)
