from pathlib import Path

path=Path(__file__).absolute().parent.parent.joinpath("font/Arial.ttf")

class DefaultSetting:
    # 服务器相关
    KEEP_ALIVE = False
    DEBUG = True
    HOST = "localhost"
    PORT = 4500
    # 数据库相关
    SQLDBURLS = dict(defaultdb="mysql://root:rstrst@localhost:3306/test_auth")
    REDIS_SETTINGS = dict(captcha="redis://localhost:6379/1", auth_token="redis://localhost:6379/2")
    # token生成相关
    SECRET_KEY = 'secret-key'
    SALT = 'sanic'
    TOKEN_LIFECYCLE = 86400
    TOKEN_REMEMBER_LIFECYCLE = 604800
    # 验证码相关
    CAPTCHA_FONT = str(path)
    CAPTCHA_LIFECYCLE = 600
