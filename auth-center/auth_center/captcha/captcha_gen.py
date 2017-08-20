"""用于生成随机验证码图片的模块
"""

import random
import string
import math
from PIL import Image,ImageDraw,ImageFont,ImageFilter

def gene_text(number=6):
    """生成随机字符"""
    source = string.ascii_letters+string.digits
    return ''.join(random.sample(source,number))

def gene_line(draw,width,height):
    """用来绘制干扰线
    """
    linecolor = (255,0,0)
    begin = (random.randint(0, width), random.randint(0, height))
    end = (random.randint(0, width), random.randint(0, height))
    draw.line([begin, end], fill = linecolor)

def gene_code(app,number=6):
    """用来绘制字符
    """
    #生成验证码图片的高度和宽度
    size = (120,30)
    #背景颜色，默认为白色
    bgcolor = (255,255,255)
    #字体颜色，默认为蓝色
    fontcolor = (0,0,255)
    #干扰线颜色。默认为红色

    #是否要加入干扰线
    draw_line = True
    #加入干扰线条数的上下限
    line_number = (1,5)
    width,height = size #宽和高
    font = ImageFont.truetype(app.config['CAPTCHA_FONT'],25)
    image = Image.new('RGBA',(width,height),bgcolor) #创建图片
    draw = ImageDraw.Draw(image)  #创建画笔
    text = gene_text(number) #生成字符串
    font_width, font_height = font.getsize(text)
    draw.text(((width - font_width) / number, (height - font_height) / number),text,
            font= font,fill=fontcolor) #填充字符串

    if draw_line:
        gene_line(draw,width,height)
    # image = image.transform((width+30,height+10), Image.AFFINE, (1,-0.3,0,-0.1,1,0),Image.BILINEAR)  #创建扭曲
    image = image.transform((width+20,height+10), Image.AFFINE, (1,-0.3,0,-0.1,1,0),Image.BILINEAR)  #创建扭曲
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE) #滤镜，边界加强
    return image,text
