import random
import string
import uuid
import asyncio
import aiohttp
import base64
import math
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from sanic_cors import cross_origin
from sanic import Blueprint
from sanic.response import json,html
from auth_center.model import User, Role
from auth_center.decorator.auth_check import authorized

auth = Blueprint('auth')


@auth.post("/")
async def auth_index(request):
    json_data = request.json
    username = json_data.get("username")
    password = json_data.get("password")
    try:
        user = await User.get(User.username == username)
    except Exception as e:
        return josn({"message":"UserDoesNotExist"},401)
    else:
        flag = user.password.check_password(password)
        if flag:
            roles = [i.service_name for i in  await user.roles]
            token_dic = {
                "_id":str(user._id),
                "roles":roles
            }
            token = request.app.serializer.dumps(token_dic)
            return json({"message":token})
        else:
            return josn({"message":"password not match"},401)


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

def gene_code(number=6):
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
    font = ImageFont.truetype('arial.ttf',25)
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

@auth.post("/captcha")
async def auth_captcha(request):
    id_ = uuid.uuid4()
    img,text = gene_code()
    await request.app.redis["captcha"].set(id_,text)
    await request.app.redis["captcha"].expire(id_,600)
    with BytesIO() as f:
        img.save(f,'png')
        b = base64.b64encode(f.getvalue())
    return json({"message":{'captcha_id':str(id_),'content':b}})
