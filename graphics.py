import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def get_template_path(base_name):
    # Проверяем все возможные варианты написания расширений
    for ext in ['.jpeg', '.jpg', '.PNG', '.JPEG', '.JPG', '.png']:
        path = f"{base_name}{ext}"
        if os.path.exists(path):
            return path
    return None

def generate_certificate(cert_type, name1, name2):
    template_path = get_template_path(f"{cert_type}_template")
    output_path = "certificate_output.png"
    
    if not template_path:
        # Если бот не видит твои картинки, он создаст ядовито-зеленый квадрат
        # Это сразу покажет нам, что дело в имени файлов на GitHub
        img = Image.new("RGB", (1000, 1000), color=(0, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.text((500, 500), f"ОШИБКА: Файл {cert_type}_template не найден!", fill=(0,0,0), anchor="mm")
    else:
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # Используем встроенный шрифт, но увеличиваем его размер в 4 раза для видимости
    font = ImageFont.load_default(size=40)

    width, height = img.size
    center_x = width // 2

    # Пишем только ники крупным шрифтом по центру
    text_line = f"@{name1}  и  @{name2}"
    
    # Координаты: ровно по центру экрана (50% ширины, 50% высоты)
    draw.text((center_x, height // 2), text_line, fill=(0, 0, 0), anchor="mm", font=font)
    draw.text((center_x, height - 100), f"Дата: {current_date}", fill=(100, 100, 100), anchor="mm", font=font)
    
    img.save(output_path)
    return output_path
