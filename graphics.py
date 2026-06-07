import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def get_template_path(base_name):
    """Ищет файл шаблона с расширением .jpeg или .jpg"""
    for ext in ['.jpeg', '.jpg', '.JPEG', '.JPG']:
        path = f"{base_name}{ext}"
        if os.path.exists(path):
            return path
    return None

def generate_certificate(cert_type, name1, name2):
    """
    cert_type: 'marriage', 'divorced'
    name1, name2: Ники пользователей
    """
    template_path = get_template_path(f"{cert_type}_template")
    output_path = "certificate_output.png"
    
    if not template_path:
        # Режим защиты: если картинка не найдена, создается чистый бланк
        img = Image.new("RGB", (1024, 1024), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
    else:
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
    width, height = img.size
    center_x = width // 2
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # Загружаем встроенный шрифт с точным фиксированным размером (как на образце)
    try:
        font_names = ImageFont.load_default(size=46) 
        font_date = ImageFont.load_default(size=24)
    except IOError:
        font_names = ImageFont.load_default()
        font_date = ImageFont.load_default()

    # Идеальный глубокий темно-коричневый/черный цвет текста (взят строго с примера)
    text_color = (26, 16, 10) 

    if cert_type == "marriage":
        # === ТОЧНЫЕ КООРДИНАТЫ ДЛЯ СВИДЕТЕЛЬСТВА О БРАКЕ ===
        text_line = f"@{name1} и @{name2}"
        
        # Ники встают строго по центру горизонтали на высоту Y=420
        draw.text((center_x, 420), text_line, fill=text_color, anchor="mm", font=font_names)
        
        # Дата в правый нижний угол на строчку [Место для даты]
        draw.text((int(width * 0.78), 922), current_date, fill=text_color, anchor="rm", font=font_date)
        
    elif cert_type == "divorced":
        # === ТОЧНЫЕ КООРДИНАТЫ ДЛЯ СВИДЕТЕЛЬСТВА О РАЗВОДЕ ===
        text_line = f"@{name1} и @{name2}"
        
        # Корректировка высоты под пустую строку в бланке развода
        draw.text((center_x, 420), text_line, fill=text_color, anchor="mm", font=font_names)
        
        # Дата для бланка развода
        draw.text((int(width * 0.78), 922), current_date, fill=text_color, anchor="rm", font=font_date)
    
    img.save(output_path)
    return output_path
