from .default import DefaultSetting


class LocalEnv(DefaultSetting):
    HOST = "0.0.0.0"
    SQLDBURLS = dict(defaultdb="mysql://root:hsz881224@127.0.0.1:3306/test_auth")
