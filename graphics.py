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
        # Не убиваемый режим: если картинки нет, создаем аварийный бланк
        img = Image.new("RGB", (1024, 1024), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        font_err = ImageFont.load_default(size=40)
        draw.text((512, 512), f"ОШИБКА: {cert_type}_template.jpeg\nне найден на GitHub!", fill=(255,0,0), anchor="mm", font=font_err, align="center")
        img.save(output_path)
        return output_path

    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # Пытаемся загрузить встроенный шрифт и делаем его крупным
    # В будущем сюда можно подставить красивый .ttf шрифт
    try:
        font_names = ImageFont.load_default(size=48) # Крупный шрифт для ников
        font_date = ImageFont.load_default(size=36)  # Чуть мельче для даты
    except IOError:
        font_names = ImageFont.load_default()
        font_date = ImageFont.load_default()

    # Красивый темно-коричневый цвет текста под старину
    text_color = (60, 35, 20) 

    if cert_type == "marriage":
        # === КООРДИНАТЫ ДЛЯ СВИДЕТЕЛЬСТВА О БРАКЕ ===
        
        # 1. Ники по центру (X=50% ширины), высота Y=445 (ровно в пустое поле)
        draw.text((width // 2, 445), f"@{name1} и @{name2}", fill=text_color, anchor="mm", font=font_names)
        
        # 2. Дата в правый нижний угол (X=80% ширины, Y=805), выравнивание по правому краю (anchor="rm")
        draw.text((int(width * 0.8), 805), current_date, fill=text_color, anchor="rm", font=font_date)
        
    elif cert_type == "divorced":
        # === КООРДИНАТЫ ДЛЯ СВИДЕТЕЛЬСТВА О РАЗВОДЕ ===
        
        # 1. Ники по центру (X=50% ширины), высота Y=410 (в пустое поле бланка развода)
        draw.text((width // 2, 410), f"@{name1} и @{name2}", fill=text_color, anchor="mm", font=font_names)
        
        # 2. Дата в правый нижний угол (X=80% ширины, Y=925)
        draw.text((int(width * 0.8), 925), current_date, fill=text_color, anchor="rm", font=font_date)
    
    img.save(output_path)
    return output_path
