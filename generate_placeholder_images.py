"""
生成伪纪录片/手机拍摄风格的占位图片
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
import os
import hashlib

def add_noise(img, intensity=0.15):
    """添加噪点"""
    pixels = img.load()
    width, height = img.size
    for i in range(width):
        for j in range(height):
            if random.random() < intensity:
                r, g, b = pixels[i, j]
                noise = random.randint(-30, 30)
                pixels[i, j] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise))
                )
    return img

def add_vignette(img):
    """添加暗角效果"""
    width, height = img.size
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    # 创建径向渐变
    for y in range(height):
        for x in range(width):
            # 计算距离中心的距离
            dx = (x - width/2) / (width/2)
            dy = (y - height/2) / (height/2)
            distance = (dx**2 + dy**2)**0.5
            # 暗角强度
            brightness = max(0, 255 - int(distance * 180))
            draw.point((x, y), fill=brightness)
    
    # 应用暗角
    vignette = Image.new('RGB', img.size, (0, 0, 0))
    return Image.composite(img, vignette, mask)

def apply_halftone_effect(img, sample=8):
    """
    应用半色调/网点效果 - Brutalism风格的关键
    """
    width, height = img.size
    img_small = img.resize((width // sample, height // sample), Image.Resampling.LANCZOS)
    
    # 创建新图片
    result = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(result)
    
    # 为每个采样点绘制圆点
    for y in range(img_small.height):
        for x in range(img_small.width):
            pixel_value = img_small.getpixel((x, y))
            # 根据亮度计算圆点大小
            dot_size = int((1 - pixel_value / 255) * sample * 0.9)
            
            if dot_size > 0:
                x_pos = x * sample + sample // 2
                y_pos = y * sample + sample // 2
                draw.ellipse([
                    x_pos - dot_size, y_pos - dot_size,
                    x_pos + dot_size, y_pos + dot_size
                ], fill=0)
    
    return result

def create_found_footage_image(filename, text, scene_type='dark'):
    """创建伪纪录片风格图片"""
    # 创建图片
    width, height = 800, 600
    
    # 基础色调
    if scene_type == 'dark':
        bg_color = (20, 20, 25)
        fg_color = (200, 200, 205)
        accent_color = (120, 30, 30)  # 暗红色
    elif scene_type == 'indoor':
        bg_color = (60, 55, 50)
        fg_color = (180, 175, 170)
        accent_color = (80, 70, 50)
    elif scene_type == 'outdoor':
        bg_color = (70, 70, 75)
        fg_color = (190, 190, 195)
        accent_color = (50, 50, 60)
    else:
        bg_color = (30, 30, 35)
        fg_color = (185, 185, 190)
        accent_color = (90, 40, 40)
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 添加更强的渐变背景效果
    for y in range(height):
        gradient_factor = y / height
        color_variation = int(gradient_factor * 40)
        current_color = tuple(max(0, min(255, c + color_variation)) for c in bg_color)
        draw.rectangle([(0, y), (width, y+1)], fill=current_color)
    
    # 添加明显的视觉元素 - 矩形和线条（模拟墙壁、门框、窗户等）
    num_shapes = random.randint(8, 15)
    for _ in range(num_shapes):
        shape_type = random.choice(['rect', 'rect', 'line', 'ellipse'])  # 矩形概率更高
        
        if shape_type == 'rect':
            x1, y1 = random.randint(0, width-100), random.randint(0, height-100)
            w, h = random.randint(100, 300), random.randint(80, 250)
            # 创建更明显的明暗对比
            brightness = random.choice([-60, -40, 40, 60])
            rect_color = tuple(max(0, min(255, c + brightness)) for c in bg_color)
            draw.rectangle([x1, y1, x1+w, y1+h], fill=rect_color, outline=fg_color, width=2)
        elif shape_type == 'line':
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            line_color = tuple(max(0, min(255, c + random.randint(-30, 30))) for c in fg_color)
            draw.line([x1, y1, x2, y2], fill=line_color, width=random.randint(3, 8))
        else:
            x, y = random.randint(50, width-150), random.randint(50, height-150)
            w, h = random.randint(60, 150), random.randint(60, 150)
            brightness = random.choice([-50, -30, 30, 50])
            ellipse_color = tuple(max(0, min(255, c + brightness)) for c in bg_color)
            draw.ellipse([x, y, x+w, y+h], fill=ellipse_color, outline=accent_color, width=2)
    
    # 添加一些"抓痕"或"裂纹"效果
    for _ in range(random.randint(3, 7)):
        x_start = random.randint(0, width)
        y_start = random.randint(0, height)
        for i in range(random.randint(5, 15)):
            x_end = x_start + random.randint(-30, 30)
            y_end = y_start + random.randint(10, 40)
            draw.line([x_start, y_start, x_end, y_end], fill=accent_color, width=random.randint(1, 3))
            x_start, y_start = x_end, y_end
    
    # 添加拼贴风格元素
    # 1. 胶带痕迹
    if random.random() > 0.3:
        tape_angle = random.choice([-15, -10, 10, 15])
        tape_x = random.randint(width//4, width*3//4)
        tape_y = random.choice([20, height-40])
        tape_width = random.randint(80, 150)
        # 半透明黄色胶带
        tape_color = (200, 200, 150, 150)
        draw.rectangle([tape_x, tape_y, tape_x+tape_width, tape_y+20], 
                      fill=(220, 220, 180), outline=(180, 180, 140), width=2)
    
    # 2. 标记/圆圈
    if random.random() > 0.4:
        warning_x = random.randint(width//4, width*3//4)
        warning_y = random.randint(height//4, height*3//4)
        warning_size = random.randint(60, 120)
        # 红色圆圈标记
        for i in range(3):
            draw.ellipse([warning_x-warning_size-i*2, warning_y-warning_size-i*2, 
                         warning_x+warning_size+i*2, warning_y+warning_size+i*2], 
                        outline=(180, 20, 20), width=3)
    
    # 3. 箭头标记
    if random.random() > 0.5:
        arrow_x = random.randint(50, width-100)
        arrow_y = random.randint(50, height-100)
        # 简单箭头
        draw.line([arrow_x, arrow_y, arrow_x+40, arrow_y], fill=(180, 20, 20), width=4)
        draw.line([arrow_x+40, arrow_y, arrow_x+30, arrow_y-10], fill=(180, 20, 20), width=4)
        draw.line([arrow_x+40, arrow_y, arrow_x+30, arrow_y+10], fill=(180, 20, 20), width=4)
    
    # 4. "证据"印章
    if random.random() > 0.6:
        stamp_x = random.choice([30, width-120])
        stamp_y = random.choice([30, height-120])
        stamp_texts = ['EVIDENCE', '证据', 'CLASSIFIED', '机密', 'TOP SECRET']
        stamp_text = random.choice(stamp_texts)
        try:
            stamp_font = ImageFont.truetype("msyh.ttc", 24)
        except:
            stamp_font = small_font
        # 旋转印章效果
        draw.text((stamp_x, stamp_y), stamp_text, fill=(150, 20, 20), font=stamp_font)
    
    # 添加文字（模拟拍摄对象）
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("msyh.ttc", 48)  # 增大字体
        small_font = ImageFont.truetype("msyh.ttc", 28)
        tiny_font = ImageFont.truetype("msyh.ttc", 20)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        tiny_font = ImageFont.load_default()
    
    # 主要文字 - 添加背景框
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # 文字背景半透明框
    padding = 20
    draw.rectangle([text_x - padding, text_y - padding, 
                   text_x + text_width + padding, text_y + text_height + padding],
                  fill=(0, 0, 0), outline=accent_color, width=3)
    
    # 添加文字多重阴影（增强可见度）
    for offset in [(3, 3), (2, 2), (1, 1)]:
        draw.text((text_x + offset[0], text_y + offset[1]), text, fill=(0, 0, 0), font=font)
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)  # 纯白色主文字
    
    # 添加时间戳（手机拍摄特征）- 左下角带背景
    timestamp = f"2025/11/{random.randint(1,8):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}"
    time_bbox = draw.textbbox((0, 0), timestamp, font=small_font)
    time_w = time_bbox[2] - time_bbox[0]
    time_h = time_bbox[3] - time_bbox[1]
    draw.rectangle([10, height-50, 20+time_w, height-10], fill=(0, 0, 0, 180))
    draw.text((15, height - 45), timestamp, fill=(255, 200, 0), font=small_font)
    
    # 添加手机型号水印 - 右下角
    phones = ["iPhone 12", "iPhone 13", "Samsung Galaxy", "HUAWEI", "Xiaomi"]
    phone_model = random.choice(phones)
    phone_bbox = draw.textbbox((0, 0), phone_model, font=tiny_font)
    phone_w = phone_bbox[2] - phone_bbox[0]
    draw.rectangle([width-phone_w-20, height-35, width-5, height-5], fill=(0, 0, 0, 180))
    draw.text((width - phone_w - 15, height - 30), phone_model, fill=(180, 180, 180), font=tiny_font)
    
    # 添加"拍摄质量指示器"
    quality_text = random.choice(["低光模式", "夜间模式", "HDR关闭", "闪光灯强制", "手动对焦"])
    draw.text((15, 15), quality_text, fill=(200, 200, 0), font=tiny_font)
    
    # 应用强烈的Brutalism效果
    # 1. 先转为灰度（黑白效果）
    img = img.convert('L')
    
    # 2. 增强对比度（类似高对比度复印）
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    
    # 3. 调整亮度
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.85)
    
    # 4. 应用半色调/网点效果（Halftone）
    img = apply_halftone_effect(img)
    
    # 转回RGB用于后续处理
    img = img.convert('RGB')
    
    # 5. 添加扫描线效果（强化版）
    draw = ImageDraw.Draw(img)
    for y in range(0, height, 3):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0), width=1)
    
    # 6. 添加垂直扫描线（模拟CRT显示器）
    if random.random() > 0.5:
        for x in range(0, width, random.randint(4, 8)):
            draw.line([(x, 0), (x, height)], fill=(20, 20, 20), width=1)
    
    # 7. 添加强噪点
    img = add_noise(img, intensity=0.35)
    
    # 8. 添加暗角
    img = add_vignette(img)
    
    # 保存
    output_path = os.path.join('static', 'evidence', filename)
    img.save(output_path, quality=65)  # 低质量，模拟压缩
    print(f"✅ 生成: {output_path}")

# 生成所有占位图片
def generate_all_images():
    print("🎬 开始生成伪纪录片风格图片...")
    
    images = [
        ('fish_tank_night.jpg', '诡异的鱼缸', 'dark'),
        ('wall_scratch.jpg', '墙上抓痕', 'indoor'),
        ('old_note.jpg', '神秘纸条', 'indoor'),
        ('theater_last_row.jpg', '最后一排座位', 'dark'),
        ('theater_demolition.jpg', '拆除现场', 'outdoor'),
        ('minibus_interior.jpg', '红色小巴内部', 'dark'),
        ('gps_location.jpg', 'GPS异常定位', 'indoor'),
        ('pier_distance.jpg', '废弃码头', 'outdoor'),
        ('newspaper_1987.jpg', '1987年旧报纸', 'indoor'),
    ]
    
    for filename, text, scene_type in images:
        create_found_footage_image(filename, text, scene_type)
    
    print(f"\n✅ 所有图片生成完成！共 {len(images)} 张")

def generate_story_evidence_images(story_title, story_content, story_category, num_images=3):
    """
    根据故事内容生成相关的证据图片
    返回生成的图片文件名列表
    """
    # 根据故事内容生成唯一的文件名
    story_hash = hashlib.md5((story_title + story_content).encode()).hexdigest()[:8]
    
    # 根据类别和内容关键词选择场景类型和文字
    category_themes = {
        'cursed_object': [
            ('诡异物品', 'dark'),
            ('异常现象', 'dark'),
            ('未知来源', 'indoor')
        ],
        'abandoned_building': [
            ('废弃场所', 'dark'),
            ('禁止进入', 'outdoor'),
            ('危险区域', 'dark')
        ],
        'time_anomaly': [
            ('时间异常', 'indoor'),
            ('空间扭曲', 'dark'),
            ('失踪地点', 'outdoor')
        ],
        'supernatural_encounter': [
            ('目击现场', 'dark'),
            ('异常痕迹', 'indoor'),
            ('未解之谜', 'dark')
        ],
        'urban_legend': [
            ('都市传说', 'dark'),
            ('现场拍摄', 'indoor'),
            ('真实记录', 'outdoor')
        ]
    }
    
    # 获取该类别的主题，如果没有则使用默认
    themes = category_themes.get(story_category, [
        ('现场记录', 'dark'),
        ('证据拍摄', 'indoor'),
        ('真实影像', 'outdoor')
    ])
    
    # 从故事内容中提取关键词来生成更相关的文字
    keywords = extract_keywords_from_story(story_content)
    
    generated_files = []
    
    for i in range(min(num_images, 5)):  # 最多5张
        # 随机选择主题或使用关键词
        if keywords and random.random() > 0.3:
            text = random.choice(keywords)
            scene_type = random.choice(['dark', 'indoor', 'outdoor'])
        else:
            text, scene_type = random.choice(themes)
        
        filename = f"evidence_{story_hash}_{i+1}.jpg"
        create_found_footage_image(filename, text, scene_type)
        generated_files.append(filename)
    
    return generated_files

def extract_keywords_from_story(content):
    """从故事内容中提取可用作图片主题的关键词"""
    keywords = []
    
    # 常见的恐怖/灵异关键词
    keyword_patterns = [
        '鱼缸', '墙壁', '座位', '戏院', '小巴', '码头', 
        '纸条', '照片', '录像', '监控', '手机', '镜子',
        '房间', '走廊', '楼梯', '地下室', '天台', '电梯',
        '抓痕', '血迹', '脚印', '影子', '雾气', '窗户',
        '门', '钟声', '脚步声', '呼吸', '眼睛', '手印'
    ]
    
    for keyword in keyword_patterns:
        if keyword in content:
            keywords.append(keyword)
    
    return keywords[:10]  # 最多返回10个关键词

def create_abstract_image(filename, color_scheme='dark'):
    """
    创建抽象恐怖风格图片 - 加强版
    """
    width, height = 800, 600
    
    # 颜色方案 - 增强对比度
    color_schemes = {
        'dark': [(15, 15, 20), (50, 50, 55), (100, 100, 105), (150, 30, 30)],  # 添加红色
        'blood': [(60, 15, 15), (120, 30, 30), (180, 50, 50), (220, 80, 80)],
        'cold': [(20, 25, 40), (40, 50, 75), (60, 75, 110), (80, 100, 140)],
        'decay': [(50, 55, 45), (80, 85, 70), (110, 115, 95), (140, 145, 120)]
    }
    
    colors = color_schemes.get(color_scheme, color_schemes['dark'])
    
    img = Image.new('RGB', (width, height), colors[0])
    draw = ImageDraw.Draw(img)
    
    # 添加渐变背景
    for y in range(height):
        factor = y / height
        color_idx = int(factor * (len(colors) - 1))
        next_idx = min(color_idx + 1, len(colors) - 1)
        local_factor = (factor * (len(colors) - 1)) - color_idx
        
        r = int(colors[color_idx][0] * (1 - local_factor) + colors[next_idx][0] * local_factor)
        g = int(colors[color_idx][1] * (1 - local_factor) + colors[next_idx][1] * local_factor)
        b = int(colors[color_idx][2] * (1 - local_factor) + colors[next_idx][2] * local_factor)
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 创建大量明显的图案元素
    for _ in range(random.randint(25, 40)):
        shape_type = random.choice(['ellipse', 'rectangle', 'line', 'polygon'])
        color = random.choice(colors)
        
        if shape_type == 'ellipse':
            x1, y1 = random.randint(-100, width), random.randint(-100, height)
            x2, y2 = x1 + random.randint(80, 400), y1 + random.randint(80, 400)
            # 添加轮廓增强可见度
            draw.ellipse([x1, y1, x2, y2], fill=color, outline=colors[-1], width=3)
        elif shape_type == 'rectangle':
            x1, y1 = random.randint(-50, width), random.randint(-50, height)
            x2, y2 = x1 + random.randint(100, 350), y1 + random.randint(100, 350)
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=colors[-1], width=4)
        elif shape_type == 'polygon':
            points = [(random.randint(0, width), random.randint(0, height)) 
                     for _ in range(random.randint(3, 6))]
            draw.polygon(points, fill=color, outline=colors[-1])
        else:
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            draw.line([x1, y1, x2, y2], fill=colors[-1], width=random.randint(5, 15))
    
    # 添加"扭曲"效果 - 随机曲线
    for _ in range(random.randint(10, 20)):
        points = []
        x_start = random.randint(0, width)
        y_start = random.randint(0, height)
        for i in range(random.randint(5, 10)):
            x_start += random.randint(-50, 50)
            y_start += random.randint(-50, 50)
            points.append((x_start, y_start))
        if len(points) > 1:
            draw.line(points, fill=colors[-1], width=random.randint(2, 6))
    
    # 添加"噪音纹理"
    for _ in range(random.randint(50, 100)):
        x, y = random.randint(0, width), random.randint(0, height)
        size = random.randint(2, 8)
        noise_color = random.choice(colors)
        draw.ellipse([x, y, x+size, y+size], fill=noise_color)
    
    # 应用效果
    img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(2, 5)))
    img = add_noise(img, intensity=0.3)
    
    # 降低亮度
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.6)
    
    # 添加扫描线效果
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0), width=1)
    
    # 保存
    output_path = os.path.join('static', 'evidence', filename)
    img.save(output_path, quality=60)
    print(f"✅ 生成抽象图片: {output_path}")
    return filename

if __name__ == '__main__':
    generate_all_images()
