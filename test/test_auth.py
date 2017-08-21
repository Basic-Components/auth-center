import unittest
from test.setup_mixin import SetUpAPPMixin
class Test_auth(unittest.TestCase,SetUpAPPMixin):
    
    def test_auth(self):
        q = self.app.test_client.post("/captcha",json={"type": "signup"})
        
    def test_signup(self):
        pass