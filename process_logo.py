from PIL import Image

def remove_white_background(img_path, output_path, threshold=240):
    img = Image.open(img_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # Change all white pixels (above threshold) to transparent
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    
    # Crop to content to remove excess transparent padding around the logo
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    img.save(output_path, "PNG")

if __name__ == "__main__":
    input_file = '/home/gaintcev/.gemini/antigravity/brain/3797c5b9-d6ac-4c32-bbd2-484dc01c5f38/media__1772495586347.png'
    output_file = '/home/gaintcev/Рабочий стол/site2/img/logo.png'
    remove_white_background(input_file, output_file, threshold=245)
    print("New PF Logo background removed, cropped, and saved to img/logo.png")
