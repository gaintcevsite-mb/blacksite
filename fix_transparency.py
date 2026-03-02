from PIL import Image
import os
import glob

def make_transparent(file_path):
    print(f"Processing {file_path}")
    img = Image.open(file_path)
    img = img.convert("RGBA")
    datas = img.getdata()
    
    newData = []
    for item in datas:
        # Distance to white
        r, g, b, a = item
        # If it's a very light pixel (background or glare), turn it transparent
        if r > 240 and g > 240 and b > 240:
            newData.append((255, 255, 255, 0))
        elif r > 230 and g > 230 and b > 230:
            newData.append((r, g, b, 100)) # Semi transparent edge
        else:
            newData.append((r, g, b, a))
            
    img.putdata(newData)
    img.save(file_path, "PNG")

for fn in glob.glob("img/*.png"):
    make_transparent(fn)

print("Transparency processing complete.")
