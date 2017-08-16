from .default import DefaultSetting


class TestingEnv(DefaultSetting):
    SQLDBURLS = dict(defaultdb="mysql://root:h7wFdCZN2NubZonbXAs1mYUf@114.55.125.148:3306/micro_auth")
    REDIS_SETTINGS = dict(captcha="redis://:h7wFdCZN2NubZonbXAs1mYUf@114.55.125.148:6379/7", auth_token="redis://:h7wFdCZN2NubZonbXAs1mYUf@114.55.125.148:6379/7")
    HOST = "0.0.0.0"
    PORT = 4567
