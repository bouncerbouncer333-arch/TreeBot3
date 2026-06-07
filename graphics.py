import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def get_template_path(base_name):
    for ext in ['.jpeg', '.jpg', '.png']:
        path = f"{base_name}{ext}"
        if os.path.exists(path):
            return path
    return None

def generate_certificate(cert_type, name1, name2):
    template_path = get_template_path(f"{cert_type}_template")
    output_path = "certificate_output.png"
    
    # Если картинка вдруг не найдена, создаем белый бланк, чтобы бот не ломался
    if not template_path:
        img = Image.new("RGB", (1000, 700), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
    else:
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # Попробуем загрузить стандартный крупный шрифт. Если на сервере его нет, PIL подставит базовый
    try:
        font_names = ImageFont.load_default() # Позже сюда можно будет загрузить красивый шрифт .ttf
    except IOError:
        font_names = ImageFont.load_default()

    # Получаем ширину и высоту загруженного изображения для центрирования
    width, height = img.size
    center_x = width // 2

    # Логика размещения текста на бланках
    if cert_type == "marriage":
        # Текст для свидетельства о браке
        # name1 и name2 будут вписаны крупно по центру друг под другом или в одну строку
        text_line = f"@{name1}  и  @{name2}"
        
        # Координаты: центр по горизонтали, а по вертикали — примерно чуть ниже середины (измени 450 под свое поле)
        draw.text((center_x, 430), text_line, fill=(40, 20, 20), align="center", anchor="mm")
        # Дата внизу бланка (измени 600 под свое поле)
        draw.text((center_x, 600), f"Дата: {current_date}", fill=(100, 100, 100), anchor="mm")
        
    elif cert_type == "divorced":
        # Текст для свидетельства о разводе
        text_line = f"@{name1}  и  @{name2}"
        
        # Координаты для развода (настраиваем высоту под пустое место на твоем втором бланке)
        draw.text((center_x, 430), text_line, fill=(50, 50, 50), align="center", anchor="mm")
        draw.text((center_x, 600), f"Дата расторжения: {current_date}", fill=(120, 120, 120), anchor="mm")
    
    img.save(output_path)
    return output_path
