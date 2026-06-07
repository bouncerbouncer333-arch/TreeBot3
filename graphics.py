import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def get_template_path(base_name):
    for ext in ['.jpeg', '.jpg', '.JPEG', '.JPG']:
        path = f"{base_name}{ext}"
        if os.path.exists(path):
            return path
    return None

def generate_certificate(cert_type, name1, name2):
    template_path = get_template_path(f"{cert_type}_template")
    output_path = "certificate_output.png"
    
    if not template_path:
        img = Image.new("RGB", (1024, 1024), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
    else:
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
    width, height = img.size
    center_x = width // 2
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    try:
        font_names = ImageFont.load_default(size=46) 
        font_date = ImageFont.load_default(size=24)
    except IOError:
        font_names = ImageFont.load_default()
        font_date = ImageFont.load_default()

    text_color = (26, 16, 10) 

    if cert_type == "marriage":
        # === ТОЧНЫЕ КООРДИНАТЫ И СИМВОЛ ДЛЯ БРАКА ===
        text_line = f"@{name1}  ❤  @{name2}"
        
        draw.text((center_x, 420), text_line, fill=text_color, anchor="mm", font=font_names)
        draw.text((int(width * 0.78), 922), current_date, fill=text_color, anchor="rm", font=font_date)
        
    elif cert_type == "divorced":
        # === ТОЧНЫЕ КООРДИНАТЫ И СИМВОЛ ДЛЯ РАЗВОДА ===
        text_line = f"@{name1}  💔  @{name2}"
        
        draw.text((center_x, 420), text_line, fill=text_color, anchor="mm", font=font_names)
        draw.text((int(width * 0.78), 922), current_date, fill=text_color, anchor="rm", font=font_date)
    
    img.save(output_path)
    return output_path
