import os
import PIL.Image as Image

input_path = '/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/media__1772663052753.png'
out_dir = '/home/gaintcev/Рабочий стол/site2/extracted_cubes2'
os.makedirs(out_dir, exist_ok=True)

img = Image.open(input_path).convert("RGBA")
width, height = img.size

# It's a 3x6 grid
rows = 3
cols = 6

cell_w = width // cols
cell_h = height // rows

def make_transparent_and_trim(img_pil, tolerance=15):
    pixels = img_pil.load()
    w, h = img_pil.size
    soft_buffer = 40
    
    min_x, min_y, max_x, max_y = w, h, -1, -1
    
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r > 255 - tolerance and g > 255 - tolerance and b > 255 - tolerance:
                pixels[x, y] = (r, g, b, 0)
            else:
                if r > 255 - tolerance - soft_buffer and g > 255 - tolerance - soft_buffer and b > 255 - tolerance - soft_buffer:
                    brightness = (r + g + b) / 3.0
                    alpha = int(255 - ((brightness - (255 - tolerance - soft_buffer)) / soft_buffer) * 255)
                    alpha = max(0, min(255, alpha))
                    pixels[x, y] = (r, g, b, alpha)
                    
            # Track bounds of non-transparent pixels
            if pixels[x, y][3] > 0:
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y
                
    if max_x >= min_x and max_y >= min_y:
        pad = 5
        min_x = max(0, min_x - pad)
        min_y = max(0, min_y - pad)
        max_x = min(w, max_x + pad)
        max_y = min(h, max_y + pad)
        return img_pil.crop((min_x, min_y, max_x, max_y)), True
    return img_pil, False

idx = 0
for r in range(rows):
    for c in range(cols):
        x1 = c * cell_w
        y1 = r * cell_h
        x2 = x1 + cell_w
        y2 = y1 + cell_h
        
        cell = img.crop((x1, y1, x2, y2))
        trans_cell, has_content = make_transparent_and_trim(cell)
        
        if has_content:
            out_path = os.path.join(out_dir, f'cube_{idx:02d}.png')
            trans_cell.save(out_path)
            print(f"Saved {out_path}")
            idx += 1
