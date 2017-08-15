from .default import DefaultSetting


class TestingEnv(DefaultSetting):
    SQLDBURLS = dict(defaultdb="mysql://root:hsz881224@127.0.0.1:3306/test_auth")
