from .default import DefaultSetting


class TestingEnv(DefaultSetting):
    SQLDBURLS = dict(defaultdb="mysql://root:hsz881224@192.168.1.102:3306/micro_auth")
    REDIS_SETTINGS = dict(captcha="redis://192.168.1.102:6379/1", auth_token="redis://192.168.1.102:6379/1")
    HOST = "0.0.0.0"
