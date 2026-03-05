import PIL.Image as Image

def make_transparent(input_path, output_path, tolerance=25):
    try:
        img = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {input_path}: {e}")
        return
        
    # Process pixel by pixel
    pixels = img.load()
    width, height = img.size
    
    soft_buffer = 40
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            
            # White background threshold
            if r > 255 - tolerance and g > 255 - tolerance and b > 255 - tolerance:
                pixels[x, y] = (r, g, b, 0)
            else:
                # Soft edges
                if r > 255 - tolerance - soft_buffer and g > 255 - tolerance - soft_buffer and b > 255 - tolerance - soft_buffer:
                    brightness = (r + g + b) / 3.0
                    alpha = int(255 - ((brightness - (255 - tolerance - soft_buffer)) / soft_buffer) * 255)
                    alpha = max(0, min(255, alpha))
                    pixels[x, y] = (r, g, b, alpha)

    img.save(output_path)
    print(f"Saved {output_path}")

images = {
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/glass_creditcard_1772661184410.png": "img/creditcard.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/glass_vault_1772661199839.png": "img/vault.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/glass_goldcoin_1772661213613.png": "img/goldcoin.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/glass_chart_1772661229429.png": "img/chart.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/glass_shield_1772661245439.png": "img/shield.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/glass_diamond_1772661260602.png": "img/gem.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/glass_briefcase_1772661275081.png": "img/briefcase.png",
    "/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/glass_piechart_1772661291619.png": "img/piechart.png"
}

for inp, out in images.items():
    make_transparent(inp, out)
