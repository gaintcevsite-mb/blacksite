import os
import PIL.Image as Image

input_path = '/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/media__1772663052753.png'
out_dir = '/home/gaintcev/Рабочий стол/site2/extracted_cubes'
os.makedirs(out_dir, exist_ok=True)

img = Image.open(input_path).convert("RGBA")
width, height = img.size
pixels = img.load()

# Find non-white pixels
non_white = []
for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        if r < 250 or g < 250 or b < 250:
            non_white.append((x, y))

# Group pixels into discrete bounding boxes (simple flood fill or clustering wouldn't be easy without recursion limit issues)
# Instead, since it's a grid, let's just find the horizontal and vertical gaps.
# Find rows with objects
row_has_obj = [False] * height
col_has_obj = [False] * width

for x, y in non_white:
    row_has_obj[y] = True
    col_has_obj[x] = True

def get_ranges(bool_array):
    ranges = []
    in_obj = False
    start = 0
    for i, val in enumerate(bool_array):
        if val and not in_obj:
            start = i
            in_obj = True
        elif not val and in_obj:
            # Require at least some size to ignore noise
            if i - start > 50:
                ranges.append((start, i))
            in_obj = False
    if in_obj:
        if len(bool_array) - start > 50:
            ranges.append((start, len(bool_array)))
    return ranges

row_ranges = get_ranges(row_has_obj)
col_ranges = get_ranges(col_has_obj)

print(f"Found {len(row_ranges)} rows and {len(col_ranges)} columns.")

def make_transparent(img_pil, tolerance=15):
    pixels = img_pil.load()
    w, h = img_pil.size
    soft_buffer = 40
    
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
    return img_pil

idx = 0
for r_idx, (y1, y2) in enumerate(row_ranges):
    for c_idx, (x1, x2) in enumerate(col_ranges):
        # Extract cell
        pad = 5
        cx1 = max(0, x1 - pad)
        cy1 = max(0, y1 - pad)
        cx2 = min(width, x2 + pad)
        cy2 = min(height, y2 + pad)
        
        crop = img.crop((cx1, cy1, cx2, cy2))
        
        # Check if cell is mostly empty
        px2 = crop.load()
        cw, ch = crop.size
        has_content = False
        content_count = 0
        for cy in range(ch):
            for cx in range(cw):
                r,g,b,a = px2[cx, cy]
                if r < 250 or g < 250 or b < 250:
                    content_count += 1
                    if content_count > 1000:
                        has_content = True
                        break
            if has_content:
                break
                
        if has_content:
            res = make_transparent(crop)
            out_path = os.path.join(out_dir, f'cube_{r_idx}_{c_idx}.png')
            res.save(out_path)
            print(f"Saved {out_path}")
            idx += 1
