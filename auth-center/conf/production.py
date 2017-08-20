from .default import DefaultSetting


class ProductionEnv(DefaultSetting):
    SQLDBURLS = dict(defaultdb="mysql://root:hsz881224@mysql:3306/micro_auth")
    REDIS_SETTINGS = dict(captcha="redis://redis:6379/1", auth_token="redis://redis:6379/1")
